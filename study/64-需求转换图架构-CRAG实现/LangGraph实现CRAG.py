import weaviate
from os import getenv
from dotenv import load_dotenv
from typing import TypedDict, List
from langchain_core.documents import Document
from weaviate.classes.init import Auth
from langchain_weaviate import WeaviateVectorStore
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langgraph.graph import StateGraph, START, END

load_dotenv()


# Agent 状态
class AgentState(TypedDict):
    question: str
    documents: List[Document]
    need_search: str
    generation: str


# 检索器
weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=getenv("WEAVIATE_CLOUD_HOST"),
    auth_credentials=Auth.api_key(getenv("WEAVIATE_CLOUD_API_KEY")),
    skip_init_checks=True,
)
vector_store = WeaviateVectorStore(
    client=weaviate_client,
    index_name="DatasetDemo",
    text_key="text",
    embedding=OpenAIEmbeddings(
        api_key=getenv("OPENAI_KEY"),
        base_url=getenv("OPENAI_API_URL"),
        model="text-embedding-3-small",
    ),
)
retriever = vector_store.as_retriever(search_type="mmr")


# 大语言模型
chat = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
)


# 检索质量评估
class GradeDocument(BaseModel):
    """文档评分Pydantic模型"""

    binary_score: str = Field(description="yes或no，表示文档是否与问题相关。")


grade_system_msg = """你是一个评估检索到的文档与用户问题相关性的评估员。
如果文档包含与问题相关的关键字或语义，请将其评级为相关。
给出一个是否相关得分为yes或者no，以表明文档是否与问题相关。
"""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", grade_system_msg),
        ("human", "检索文档：\n\n{document}\n\n用户问题：{question}"),
    ]
)
grade_chain = grade_prompt | chat.with_structured_output(GradeDocument)


# 问题重写
rewrite_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个能将输入问题优化的更好，更适合网络搜索的问题重写器。请查看输入并尝试推理潜在的语义意图/含义。",
        ),
        ("human", "这里是初始化问题：\n\n{question}\n\n请尝试提出一个改进问题。"),
    ]
)
rewrite_chain = rewrite_prompt | chat.bind(temperature=0) | StrOutputParser()


# 生成器
def format_docs(docs: List[Document]) -> str:
    return "\n\n".join([doc.page_content for doc in docs])


generate_prompt = ChatPromptTemplate.from_template(
    """你是一个回答任务的助理，使用以下检索到的上下文来回答问题。如果不知道就说不知道，不要胡编乱造，并保持答案简洁。

问题：{question}
上下文：{context}
答案："""
)
generate_chain = generate_prompt | chat.bind(temperature=0) | StrOutputParser()


# 搜索工具
class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


google_serper = GoogleSerperRun(
    name="google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具传递的参数是搜索查询语句。"
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)


# 创建Agent
graph_builder = StateGraph(AgentState)


# 检索器节点
def retriever_node(state: AgentState, config: dict):
    print("==========检索器节点==========")
    question = state["question"]
    docs = retriever.invoke(question)
    return {**state, "documents": docs}


# 评分节点
def grade_node(state: AgentState, config: dict):
    print("==========评分节点==========")
    docs = state["documents"]
    question = state["question"]
    need_search = "no"
    filter_docs = []
    for doc in docs:
        result: GradeDocument = grade_chain.invoke(
            {"document": doc.page_content, "question": question}
        )
        if result.binary_score == "no":
            print("文档不相关")
            need_search = "yes"
        else:
            print("文档相关")
            filter_docs.append(doc)
    return {**state, "documents": filter_docs, "need_search": need_search}


# 重写节点
def rewrite_node(state: AgentState, config: dict):
    print("==========重写节点==========")
    question = state["question"]
    better_question = rewrite_chain.invoke({"question": question})
    print(f"新问题: {better_question}")
    return {**state, "question": better_question}


# 网络搜索节点
def web_search_node(state: AgentState, config: dict):
    print("==========网络搜索节点==========")
    question = state["question"]
    docs = state["documents"]
    search_result = google_serper.invoke(question)
    docs.append(Document(page_content=search_result))
    print(f"搜索结果: {search_result}")
    return {**state, "documents": docs}


# 生成器节点
def generation_node(state: AgentState, config: dict):
    print("==========生成器节点==========")
    question = state["question"]
    documents = state["documents"]
    result = generate_chain.invoke(
        {"question": question, "context": format_docs(documents)}
    )
    return {**state, "generation": result}


graph_builder.add_node("retriever_node", retriever_node)
graph_builder.add_node("grade_node", grade_node)
graph_builder.add_node("rewrite_node", rewrite_node)
graph_builder.add_node("web_search_node", web_search_node)
graph_builder.add_node("generation_node", generation_node)


def grade_router(state: AgentState, config: dict) -> str:
    need_search = state["need_search"]
    if need_search == "yes":
        return "rewrite_node"
    return "generation_node"


graph_builder.add_edge(START, "retriever_node")
graph_builder.add_edge("retriever_node", "grade_node")
graph_builder.add_conditional_edges("grade_node", grade_router)
graph_builder.add_edge("rewrite_node", "web_search_node")
graph_builder.add_edge("web_search_node", "generation_node")
graph_builder.add_edge("generation_node", END)

agent = graph_builder.compile()

print(agent.invoke({"question": "能介绍一下什么是LLMOps么？"}))
