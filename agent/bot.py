from agent.helpers import assistant_message, call_tool
from agent.tools import definitions
from services.llm import Llm


class Bot:
    search_limit = 5
    response_limit = 8

    def __init__(self):
        self._llm = Llm()
        self._system_message = (
            "You are a task agent. Use the tools to read and change tasks. "
            "To find a task from the user's words, call filter_tasks_by_text "
            "with a regular expression. If the result is empty, try a different pattern. "
            f"Use at most {self.search_limit} searches, then ask the user to clarify. "
            "Reply briefly."
        )
        self._turns: list[dict] = []

    def chat(self, user_message: str) -> str:
        """Reply to one user message, running any tool calls the model requests."""
        if not isinstance(user_message, str) or user_message.strip() == "":
            raise ValueError("user_message is empty")

        self._turns.append({"role": "user", "content": user_message})
        messages: list[dict] = [
            {"role": "system", "content": self._system_message},
            *self._turns,
        ]
        searches = 0
        allow_tools = True

        for _ in range(self.response_limit):
            message = self._llm.generate_response(
                messages,
                tools=definitions if allow_tools else None,
            )
            if not message.tool_calls:
                reply = message.content or ""
                if not reply:
                    raise ValueError("model returned an empty response")
                final = {"role": "assistant", "content": reply}
                messages.append(final)
                self._turns.append(final)
                return reply

            assistant = assistant_message(message)
            messages.append(assistant)
            self._turns.append(assistant)
            for call in message.tool_calls:
                if call.function.name == "filter_tasks_by_text":
                    searches += 1
                    if searches > self.search_limit:
                        allow_tools = False
                        content = (
                            f"Search limit of {self.search_limit} reached. "
                            "Ask the user to clarify."
                        )
                    else:
                        content = call_tool(call)
                else:
                    content = call_tool(call)
                tool_message = {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": content,
                }
                messages.append(tool_message)
                self._turns.append(tool_message)

        raise ValueError("tool calls did not finish")
