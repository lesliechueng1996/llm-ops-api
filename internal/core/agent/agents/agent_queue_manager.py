"""
@Time   : 2024/12/24 14:34
@Author : Leslie
@File   : agent_queue_manager.py
"""

from queue import Queue, Empty
from uuid import UUID, uuid4
from typing import Generator
from redis import Redis
from internal.entity import InvokeFrom
from internal.core.agent.entities import AgentQueueEvent, QueueEvent
import time
import logging


class AgentQueueManager:
    q: Queue
    user_id: UUID
    task_id: UUID
    invoke_from: InvokeFrom
    redis_client: Redis

    def __init__(
        self, user_id: UUID, task_id: UUID, invoke_from: InvokeFrom, redis_client: Redis
    ):
        self.q = Queue()
        self.user_id = user_id
        self.task_id = task_id
        self.invoke_from = invoke_from
        self.redis_client = redis_client

        user_prefix = (
            "account"
            if invoke_from in [InvokeFrom.WEB_APP, InvokeFrom.DEBUGGER]
            else "end-user"
        )

        self.redis_client.setex(
            self.generate_task_belong_cache_key(task_id),
            3600,
            f"{user_prefix}-{str(user_id)}",
        )

    def listen(self) -> Generator:
        start_time = time.time()
        last_ping_time = 0
        listen_timeout = 600

        while True:
            try:
                item = self.q.get(timeout=1)
                if item is None:
                    break
                yield item
            except Empty:
                continue
            finally:
                elapsed_time = time.time() - start_time
                if elapsed_time // 10 > last_ping_time:
                    self.publish(
                        AgentQueueEvent(
                            id=uuid4(),
                            task_id=self.task_id,
                            event=QueueEvent.PING,
                        )
                    )
                    last_ping_time = elapsed_time // 10

                if elapsed_time >= listen_timeout:
                    self.publish(
                        AgentQueueEvent(
                            id=uuid4(),
                            task_id=self.task_id,
                            event=QueueEvent.TIMEOUT,
                        )
                    )

                if self._is_stopped():
                    self.publish(
                        AgentQueueEvent(
                            id=uuid4(),
                            task_id=self.task_id,
                            event=QueueEvent.STOP,
                        )
                    )

    def publish(self, agent_queue_event: AgentQueueEvent):
        logging.info(f"Publishing event: {agent_queue_event.event}")
        self.q.put(agent_queue_event)

        if agent_queue_event.event in [
            QueueEvent.STOP,
            QueueEvent.ERROR,
            QueueEvent.TIMEOUT,
            QueueEvent.AGENT_END,
        ]:
            self.stop_listen()

    def stop_listen(self):
        self.q.put(None)

    def generate_task_belong_cache_key(self, task_id: UUID):
        return f"generate_task_belong:{str(task_id)}"

    def generate_task_stopped_cache_key(self, task_id: UUID):
        return f"generate_task_stopped:{str(task_id)}"

    def _is_stopped(self) -> bool:
        task_stopped_cache_key = self.generate_task_stopped_cache_key(self.task_id)
        result = self.redis_client.get(task_stopped_cache_key)

        logging.info(f"Checking if task is stopped: {result}")

        if result is not None:
            return True
        return False
