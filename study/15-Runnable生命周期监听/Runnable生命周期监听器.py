from langchain_core.runnables import RunnableLambda, RunnableConfig
from langchain_core.tracers.schemas import Run
import time


def on_start(ru_obj: Run, config: RunnableConfig):
    print("on_start")
    print(ru_obj)
    print(config)


def on_end(ru_obj: Run, config: RunnableConfig):
    print("on_end")
    print(ru_obj)
    print(config)


def on_error(ru_obj: Run, config: RunnableConfig):
    print("on_error")
    print(ru_obj)
    print(config)


runnable = RunnableLambda(lambda x: time.sleep(2)).with_listeners(
    on_start=on_start, on_end=on_end, on_error=on_error
)

runnable.invoke(2, config={"configurable": {"name": "Leslie"}})
