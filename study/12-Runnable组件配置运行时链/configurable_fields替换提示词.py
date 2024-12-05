from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.utils import ConfigurableField

prompt = PromptTemplate.from_template("请写一个关于{name}的故事").configurable_fields(
    template=ConfigurableField(id="prompt_template")
)
prompt_value = prompt.invoke({"name": "小明"})
print(prompt_value.to_string())

changed_prompt_value = prompt.invoke(
    {"name": "小红"},
    config={"configurable": {"prompt_template": "请写一个关于{name}的笑话"}},
)
print(changed_prompt_value.to_string())

print(
    prompt.with_config(configurable={"prompt_template": "请写一个关于{name}的笑话"})
    .invoke({"name": "小红"})
    .to_string()
)
