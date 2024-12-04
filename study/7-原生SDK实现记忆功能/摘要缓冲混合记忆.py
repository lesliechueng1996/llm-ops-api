from dotenv import load_dotenv
from os import getenv
from openai import OpenAI


class ConversationSummaryBufferMemory:
    def __init__(self, summary: str = "", chat_histories: list = []) -> None:
        self.max_tokens = 300
        self.chat_histories = chat_histories
        self.summary = summary
        self._client = OpenAI(
            api_key=getenv("OPENAI_API_KEY"), base_url=getenv("OPENAI_URL")
        )

    @classmethod
    def get_num_tokens(cls, text: str) -> int:
        return len(text)

    def save_context(self, human_query: str, ai_content: str) -> None:
        # 保存新的对话信息
        self.chat_histories.append({"human": human_query, "ai": ai_content})

        tokens = self.get_num_tokens(self.get_buffer_string())

        if tokens > self.max_tokens:
            first_chat = self.chat_histories.pop(0)
            print("摘要生成中")
            self.summary = self.summary_text(
                f"Human:{first_chat['human']}\nAI:{first_chat['ai']}"
            )
            print("摘要生成完毕: ", self.summary)

    def get_buffer_string(self) -> str:
        buffer = ""
        for chat in self.chat_histories:
            buffer += f"Human:{chat['human']}\nAI:{chat['ai']}\n\n"
        return buffer.strip()

    def summary_text(self, new_chat_message: str) -> str:
        prompt = f"""你是一个强大的聊天机器人，请根据用户提供的谈话内容，总结内容，并将其添加到先前提供的摘要中，返回一个新的摘要。
        <example>
        当前摘要: 人类会问人工智能对人工智能的看法。人工智能认为人工智能是一股向善的力量。新的谈话内容：

        Human: 为什么你认为人工智能是一股向善的力量？
        AI: 因为人工智能将帮助人类充分发挥潜力。新摘要: 人类会问人工智能对人工智能的看法。人工智能认为人工智能是一股向善的力量，因为它将帮助人类充分发挥潜力。
        </example>
        ======================以下的数据是实际需要处理的内容======================

        当前摘要: {self.summary}

        新的对话内容: {new_chat_message}
        请帮用户将上面的信息生成新摘要
"""
        response = self._client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    def load_memory_variables(self):
        buffer_string = self.get_buffer_string()
        return {
            "chat_history": f"摘要:{self.summary}\n\n历史消息:{buffer_string}\n\n",
        }


client = OpenAI(api_key=getenv("OPENAI_API_KEY"), base_url=getenv("OPENAI_URL"))
memory = ConversationSummaryBufferMemory()

while True:
    query = input("Human: ")
    if query == "q":
        break

    memory_variables = memory.load_memory_variables()
    prompt = f"你是一个强大的聊天机器人, 请根据对应的上下文和用户的提问解决问题。\n\n {memory_variables.get('chat_history')} \n\n 用户提问: {query}"
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    print("AI: ", flush=True, end="")
    answer = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content is None:
            break
        answer += content
        print(content, flush=True, end="")
    print("")
    memory.save_context(query, answer)
