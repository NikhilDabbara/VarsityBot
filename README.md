# VarsityBot 

A local, privacy-first College Assistant chatbot built with **LangChain** and **Ollama**. VarsityBot uses a tool-calling agent backed by a locally-hosted `qwen2.5:3b` model to answer common student queries — attendance eligibility, result grading, fee balances, library fines, and hostel fees — by invoking deterministic calculator tools instead of letting the LLM "guess" at math.

## Why VarsityBot?

LLMs are notoriously unreliable at arithmetic. VarsityBot sidesteps that by forcing every numeric query through a dedicated Python tool, so the model's job is limited to understanding intent and formatting the final answer — not doing the math itself. Because it runs entirely on a local Ollama model, no student data ever leaves your machine.

## Features

-  **Tool-calling agent** — every calculation is delegated to a deterministic Python function, never computed by the LLM directly
-  **Attendance Calculator** — percentage + 75% exam eligibility check
-  **Result Calculator** — average, letter grade (A/B/C/D), and pass/fail status across 5 subjects
-  **Fee Balance Calculator** — pending course fee tracking
-  **Library Fine Calculator** — delayed-return fine computation
-  **Hostel Fee Calculator** — total hostel fee from monthly rate × months stayed
-  **Fully local** — runs on Ollama, no API keys, no data sent to external servers
-  **Conversational memory** — maintains chat history across the session

## Tech Stack

- [LangChain](https://www.langchain.com/) (tool-calling agent + `AgentExecutor`)
- [Ollama](https://ollama.com/) running `qwen2.5:3b`
- Python 3.10+

## Prerequisites

1. **Ollama installed and running** — [download here](https://ollama.com/download)
2. **The `qwen2.5:3b` model pulled locally:**
   ```bash
   ollama pull qwen2.5:3b
   ```
3. **Python 3.10 or higher**

## Installation

```bash
# Clone the repository
git clone https://github.com/NikhilDabbara/VarsityBot.git
cd varsitybot

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Make sure Ollama is running in the background, then:

```bash
python varsitybot.py
```

You'll be dropped into an interactive prompt:

```
You: I attended 68 out of 90 classes, am I eligible for exams?
Chatbot: Attendance Percentage: 75.56%. Status: Eligible for Exam.

You: My marks are 95, 90, 88, 91, 87 — what's my grade?
Chatbot: Average Marks: 90.20, Grade: A, Status: Pass.
```

Type `exit`, `quit`, or `bye` to end the session.

## Rules Enforced

| Tool | Rule |
|---|---|
| Attendance | ≥ 75% → Eligible, < 75% → Not Eligible |
| Result | ≥90 → A, 75–89 → B, 60–74 → C, <60 → D; Pass if average ≥ 50 |
| Fee Balance | Pending = Total Course Fee − Amount Paid |
| Library Fine | ₹5 per delayed day |
| Hostel Fee | Total = Monthly Fee × Months Stayed |

## Project Structure

```
varsitybot/
├── varsitybot.py       # Main application
├── requirements.txt    # Python dependencies
├── README.md
└── .gitignore
```

## Known Limitations

- Response quality depends on the local model (`qwen2.5:3b`) correctly interpreting intent and calling the right tool — smaller models can occasionally misfire on ambiguous queries.
- No persistent storage — chat history resets when the program exits.
- Single-user, single-session CLI tool (not designed for concurrent/multi-user deployment as-is).

## Future Improvements

- [ ] Rolling window on chat history to prevent unbounded context growth
- [ ] Configurable model name via CLI flag / env var
- [ ] Optional GUI (CustomTkinter) front-end
- [ ] Unit tests for each calculator tool
- [ ] Support for additional queries (timetable lookup, exam schedule, etc.)

## License

MIT License — feel free to fork and adapt.

## Author

Built by Sree Nikhil Chowdary Dabbara — B.Tech CSE (AI/ML), VIT Vellore.