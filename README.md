# Tool calling

A small terminal task agent for teaching how a language model calls tools. The model decides which function to use. This program runs that function and sends the result back.

The example is a todo list stored in `tasks.json`. You talk to the agent in the terminal. It can list, create, update, and delete tasks.

## What the lesson shows

- Tool schemas are sent on the API request. They are not pasted into the system message, and the model does not import the Python functions.
- A reply can be normal text, or it can be one or more tool calls.
- After a tool runs, the program must send the result back and ask the model again. The API does not do that by itself.
- Update and delete need a task id. When the user describes a task in words, the model looks it up first.
- The model can call a tool with a wrong argument. `get_todays_date` is there so "tomorrow" can be calculated from a real date instead of a guess.

`sample_chat.md` is one recorded session, including a date the model got wrong and then corrected.

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

- What tasks are still to do?
- What day is today?
- Add a task to review the lesson tomorrow.
- Mark the tutorial outline as done.
- Delete the dentist task.

Creating, updating, or deleting a task writes `tasks.json` immediately. Copy that file first if you want the original sample tasks back.

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
| `filter_tasks_by_text` | Tasks whose title or description matches a regular expression |
| `filter_tasks_by_due_date` | Tasks due on an exact date |
| `filter_tasks_by_status` | Tasks with status `todo`, `in_progress`, or `done` |
| `update_task` | Changes one or more fields of a task by id |
| `delete_task` | Removes a task by id |

The schemas the model sees, and the functions the program runs, are both in `agent/tools.py`. `definitions` is the schema list. `by_name` maps each schema name to the function.

## Task file

`tasks.json` is the database. It is a JSON array. Each task has:

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
agent/helpers.py     reading, writing, and checking tasks
services/llm.py      OpenAI client
tasks.json           task store
sample_chat.md       one example session
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

Restore `tasks.json` from the copy you made before the chat, or from git if that copy is committed.
