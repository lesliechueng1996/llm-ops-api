from langchain_core.runnables import RunnableLambda

counter = -1


def func(x):
    global counter
    counter += 1
    return x / counter


runnable = RunnableLambda(func).with_retry(stop_after_attempt=2)

print(runnable.invoke(2))
