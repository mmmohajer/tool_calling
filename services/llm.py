import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env")


class Llm:
    def __init__(self, chat_model: str = "gpt-4o"):
        api_key = os.getenv("OPEN_AI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPEN_AI_API_KEY is not set")
        self._client = OpenAI(api_key=api_key)
        self.chat_model = chat_model

    def generate_response(self, messages: list[dict], tools: list[dict] | None = None):
        if not messages:
            raise ValueError("messages are empty")

        request: dict = {"model": self.chat_model, "messages": messages}
        if tools:
            request["tools"] = tools
        response = self._client.chat.completions.create(**request)
        message = response.choices[0].message
        if not message.content and not message.tool_calls:
            raise ValueError("model returned an empty response")
        return message
