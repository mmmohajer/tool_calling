from agent.bot import Bot

bot = Bot()
print("Task agent. Type exit to stop.")

while True:
    try:
        user_message = input("You: ").strip()
    except EOFError:
        print()
        break
    if user_message.lower() in {"exit", "quit"}:
        break
    if not user_message:
        continue
    print(f"Bot: {bot.chat(user_message)}")
