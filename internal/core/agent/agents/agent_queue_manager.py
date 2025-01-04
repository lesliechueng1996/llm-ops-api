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
from internal.core.agent.entities import AgentThought, QueueEvent
import time
import logging


class AgentQueueManager:
    user_id: UUID
    invoke_from: InvokeFrom
    redis_client: Redis
    _queues: dict[str, Queue]

    def __init__(
        self,
        user_id: UUID,
        invoke_from: InvokeFrom,
    ):
        self.user_id = user_id
        self.invoke_from = invoke_from
        self._queues = {}

        from app.http.module import injector

        self.redis_client = injector.get(Redis)

    def listen(self, task_id: UUID) -> Generator:
        start_time = time.time()
        last_ping_time = 0
        listen_timeout = 600

        while True:
            try:
                item = self.queue(task_id=task_id).get(timeout=1)
                if item is None:
                    break
                yield item
            except Empty:
                continue
            finally:
                elapsed_time = time.time() - start_time
                if elapsed_time // 10 > last_ping_time:
                    self.publish(
                        AgentThought(
                            id=uuid4(),
                            task_id=task_id,
                            event=QueueEvent.PING,
                        ),
                        task_id,
                    )
                    last_ping_time = elapsed_time // 10

                if elapsed_time >= listen_timeout:
                    self.publish(
                        AgentThought(
                            id=uuid4(),
                            task_id=task_id,
                            event=QueueEvent.TIMEOUT,
                        )
                    )

                if self._is_stopped(task_id):
                    self.publish(
                        AgentThought(
                            id=uuid4(),
                            task_id=task_id,
                            event=QueueEvent.STOP,
                        )
                    )

    def publish(self, agent_queue_event: AgentThought, task_id: UUID):
        logging.info(f"Publishing event: {agent_queue_event.event}")
        self.queue(task_id).put(agent_queue_event)

        if agent_queue_event.event in [
            QueueEvent.STOP,
            QueueEvent.ERROR,
            QueueEvent.TIMEOUT,
            QueueEvent.AGENT_END,
        ]:
            self.stop_listen(task_id)

    def publish_error(self, task_id: UUID, error: Exception):
        self.publish(
            AgentThought(
                id=uuid4(),
                task_id=task_id,
                event=QueueEvent.ERROR,
                observation=str(error),
            ),
            task_id,
        )

    def stop_listen(self, task_id: UUID):
        self.queue(task_id).put(None)

    @classmethod
    def generate_task_belong_cache_key(cls, task_id: UUID):
        return f"generate_task_belong:{str(task_id)}"

    @classmethod
    def generate_task_stopped_cache_key(cls, task_id: UUID):
        return f"generate_task_stopped:{str(task_id)}"

    def _is_stopped(self, task_id: UUID) -> bool:
        task_stopped_cache_key = self.generate_task_stopped_cache_key(task_id)
        result = self.redis_client.get(task_stopped_cache_key)

        logging.info(f"Checking if task is stopped: {result}")

        if result is not None:
            return True
        return False

    def queue(self, task_id: UUID) -> Queue:
        q = self._queues.get(str(task_id))
        if not q:
            user_prefix = (
                "account"
                if self.invoke_from in [InvokeFrom.WEB_APP, InvokeFrom.DEBUGGER]
                else "end-user"
            )

            self.redis_client.setex(
                self.generate_task_belong_cache_key(task_id),
                3600,
                f"{user_prefix}-{str(self.user_id)}",
            )

            q = Queue()
            self._queues[str(task_id)] = q

        return q

    @classmethod
    def set_stop_flag(cls, task_id: UUID, invoke_from: InvokeFrom, user_id: UUID):
        from app.http.module import injector

        redis_client = injector.get(Redis)

        result = redis_client.get(cls.generate_task_belong_cache_key(task_id))
        if not result:
            return

        useruser_prefix = (
            "account"
            if invoke_from in [InvokeFrom.WEB_APP, InvokeFrom.DEBUGGER]
            else "end-user"
        )
        if result.decode("utf-8") != f"{useruser_prefix}-{str(user_id)}":
            return

        redis_client.setex(cls.generate_task_stopped_cache_key(task_id), 600, "1")
