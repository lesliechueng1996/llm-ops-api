from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults
from langchain_core.utils.function_calling import convert_to_openai_tool

question = "LangChain最新版本是多少？"

# search = DuckDuckGoSearchRun()
search = DuckDuckGoSearchResults()

print(search.name)
print(search.description)
print(search.args)
print(search.invoke(question))

openai_tool = convert_to_openai_tool(search)
print(openai_tool)
