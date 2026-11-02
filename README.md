# Tool calling

A small terminal task agent for teaching how a language model calls tools. The model decides which function to use. This program runs that function and sends the result back.

The example is a todo list stored in `tasks.json`. You talk to the agent in the terminal. It can list, create, update, and delete tasks.

## What the lesson shows

- Tool schemas are sent on the API request. They are not pasted into the system message, and the model does not import the Python functions.
- A reply can be normal text, or it can be one or more tool calls.
- After a tool runs, the program must send the result back and ask the model again. The API does not do that by itself.
- Update and delete need a task id. When the user describes a task in words, the model looks it up first.
- The model can call a tool with a wrong argument. `get_todays_date` is there so "tomorrow" can be calculated from a real date instead of a guess.

One recorded session is saved in the repo. `sample_chat.md` shows each sentence together with the tool name, arguments, and result. `sample_chat.json` is the raw message list from that session. `tasks.json` is the list before the chat. `tasks.after.json` is the list after it. The program reads and writes only `tasks.json`.

## Requirements

- Python 3.10 or newer. The code uses `list[dict]` and `str | None`. It was run with Python 3.12.
- An OpenAI API key. The default model is `gpt-4o`.
- A network connection. Every turn calls the OpenAI API.

## Setup

Run these commands from the project folder, the directory that contains `main.py`.

### macOS and Linux

```bash
python3 -m venv venv
source venv/bin/activate
cp .env.sample .env
python -m pip install -r requirements.txt
```

### Windows

PowerShell:

```powershell
py -3 -m venv venv
venv\Scripts\Activate.ps1
Copy-Item .env.sample .env
python -m pip install -r requirements.txt
```

If PowerShell blocks the activate script, run this once for your user, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Command Prompt:

```bat
py -3 -m venv venv
venv\Scripts\activate
copy .env.sample .env
python -m pip install -r requirements.txt
```

### Add the API key

Open `.env` and set the key. The name must match exactly:

```
OPEN_AI_API_KEY=sk-...
```

`.env` is listed in `.gitignore`. `.env.sample` is the empty template and is safe to commit.

Leave the virtual environment with `deactivate` on any system.

## Run

From the project folder, with the virtual environment active:

```bash
python main.py
```

```
Task agent. Type exit to stop.
You:
```

Type a message and press Enter. Type `exit` or `quit` to stop. An empty line is ignored.

Start the program from this folder. `main.py` imports `agent` and `services` from here. Starting it from another directory will fail those imports.

## Prompts to try

These match the tasks in `tasks.json`, so a new reader can replay the recorded session:

- I'd like to know what tasks do you see for me?
- I don't like to buy milk anymore, are you able to remove that task for me?
- Can you add a new task, tomorrow I'd like to go to the gym with my friends, at 3 pm
- What day is today?

Creating, updating, or deleting a task writes `tasks.json` immediately. Copy that file first if you want the starting tasks back. The committed `tasks.json` is that starting list.

## How one turn works

`agent/bot.py` keeps the conversation and runs this loop for each user message:

1. Append the user message.
2. Send the conversation and the tool definitions to the model through `services/llm.py`.
3. If the model returns text, print it and stop.
4. If the model returns tool calls, run each one from the name map in `agent/tools.py`.
5. Append each result as a `tool` message, using the id the API assigned to that call. That id is not the task id.
6. Call the model again with the updated conversation.

A single model reply can contain several tool calls. Those calls count as one model request. Each `filter_tasks_by_text` call counts separately toward the search limit.

Two limits live on `Bot`:

| Limit | Value | What it counts |
| --- | --- | --- |
| `search_limit` | 5 | `filter_tasks_by_text` calls inside one user message |
| `response_limit` | 8 | Model requests inside one user message |

After five searches, later requests in that same message are sent without tools, and the model is told to ask the user to clarify. If eight model requests still have not produced a text reply, the turn raises `tool calls did not finish`.

## Tools

| Tool | What it does |
| --- | --- |
| `get_todays_date` | Today's date as `YYYY-MM-DD` |
| `create_task` | Adds a task. The id is the last task's id plus 1, or 1 when the list is empty |
| `filter_tasks_by_text` | Tasks whose title or description matches a regular expression. The recorded chat did not use this tool |
| `filter_tasks_by_due_date` | Tasks due on an exact date |
| `filter_tasks_by_status` | Tasks with status `todo`, `in_progress`, or `done` |
| `update_task` | Changes one or more fields of a task by id |
| `delete_task` | Removes a task by id |

The schemas the model sees, and the functions the program runs, are both in `agent/tools.py`. `definitions` is the schema list. `by_name` maps each schema name to the function.

## Recorded example

The session in `sample_chat.md` and `sample_chat.json` started from the three tasks in `tasks.json`:

| id | title | status | due date |
| --- | --- | --- | --- |
| 1 | Buy groceries | `todo` | 2026-11-05 |
| 2 | Write the tutorial outline | `in_progress` | 2026-11-03 |
| 3 | Call the dentist | `done` | 2026-10-28 |

What the model did:

1. Greeted the user with no tool call.
2. Listed the tasks with three `filter_tasks_by_status` calls. The second model reply called `in_progress` and `done` together.
3. Deleted id 1 when asked to remove the milk task. It reused the id from the earlier result and removed the whole groceries task. It did not call `filter_tasks_by_text`.
4. Created the gym task as id 4 with due date `2023-11-01`. It did not check today's date first.
5. Called `get_todays_date` when asked, and got `2026-11-02`.
6. Admitted the date was wrong and waited for a yes.
7. Called `update_task` for id 4 with due date `2026-11-03`.

`tasks.after.json` is the file after those calls. Ids 2 and 3 are unchanged, id 1 is gone, and id 4 is the gym task due 2026-11-03. Running the program does not read `tasks.after.json`.

`filter_tasks_by_text` takes a regular expression. That is a separate detail from the tool-calling loop. This saved session never reaches it, because the model already had the ids from the status filters.

## Task file

`tasks.json` is the database the program uses. It is a JSON array. Each task has:

| Field | Meaning |
| --- | --- |
| `id` | Integer. Assigned on create |
| `title` | Non-empty text |
| `description` | Non-empty text |
| `status` | `todo`, `in_progress`, or `done` |
| `due_date` | `YYYY-MM-DD` |

Checks for those values live in `agent/helpers.py`. A bad value is returned to the model as the tool result text, so the model can try again.

## Project layout

```
main.py              terminal chat
agent/bot.py         conversation and tool-calling loop
agent/tools.py       tool functions and schemas
agent/helpers.py     task checks, assistant messages, and tool execution
services/llm.py      OpenAI client
tasks.json           task store the program reads and writes
tasks.after.json     tasks.json after the recorded chat
sample_chat.md       that chat, with each call and result
sample_chat.json     the raw messages from that chat
.env.sample          environment template
requirements.txt     python-dotenv and openai==1.82.1
```

The default model is the `chat_model` argument of `Llm` in `services/llm.py`. `main.py` uses that default.

## Troubleshooting

**`OPEN_AI_API_KEY is not set`**

`.env` is missing, the process was started outside this folder, or the variable name does not match `.env.sample`.

**`ModuleNotFoundError: No module named 'agent'` or `'services'`**

The shell is not in the project folder. Change to the folder that contains `main.py` and run it again.

**`No module named 'dotenv'` or `'openai'`**

The virtual environment is not active, or the requirements were not installed into it. Activate `venv`, then run `python -m pip install -r requirements.txt`.

**The agent changed a task you wanted to keep**

Replace `tasks.json` with the committed starting file. `tasks.after.json` is the ending list from the recorded chat, not a second database.
