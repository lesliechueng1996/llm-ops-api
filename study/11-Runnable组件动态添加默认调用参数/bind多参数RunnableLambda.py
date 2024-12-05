from langchain_core.runnables import RunnableLambda


def get_weathre(location: str, unit: str, name: str):
    return f"{name}在{location}的天气是晴天，温度是20{unit}"


runnable = RunnableLambda(get_weathre).bind(unit="摄氏度", name="小明")
print(runnable.kwargs)

content = runnable.invoke("北京")
print(content)
