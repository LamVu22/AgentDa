# AgentA

AgentA is a multi-agent AI system that connects to your Canvas LMS account, reads your upcoming assignments, and builds a personalized day-by-day study plan. It runs entirely on your machine — your Canvas data and study plans never leave your computer.

---

## The problem it solves

Canvas posts assignments across five or six courses at once. Due dates get buried. It is easy to forget something exists until the night before it is due. AgentA reads everything for you, filters out what is already submitted or overdue, and tells you exactly what to work on and when.

---

## How it works

AgentA runs a crew of six AI agents in sequence, each with a specific job:

1. **Canvas Fetcher** — connects to the Canvas API and pulls all courses for the current enrolled semester, then fetches every upcoming unsubmitted assignment across all of them.

2. **Assignment Summarizer** — takes the raw Canvas data and rewrites each assignment in plain English, estimates how long it will take, and flags anything with a vague or missing description.

3. **Priority Ranker** — orders every assignment by a combination of urgency, point value, and estimated effort so you always know what to do first.

4. **Conflict Detector** — finds days and weeks where deadlines cluster and recommends which assignments to start early before the crunch hits.

5. **Study Planner** — uses today's date, the priority ranking, and the conflict report to build a day-by-day study plan that respects your daily hour limit and leaves a buffer before every deadline.

6. **Reminder Scheduler** — formats the final plan into a clean weekly checklist you can save or print.

---

## Requirements

- Python 3.10 or higher
- An OpenAI API key
- A Canvas personal access token
- Ollama (optional — can be used instead of OpenAI)

---

## Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/yourname/agenta.git
cd agenta
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy the environment template and fill in your credentials:

```bash
cp .env.example .env
```

Open `.env` and add:

```
CANVAS_BASE_URL=https://your-school.instructure.com
CANVAS_API_TOKEN=your_canvas_token_here
OPENAI_API_KEY=your_openai_key_here
CANVAS_TERM=Spring Semester 2026
PLANNING_HORIZON_DAYS=14
MAX_STUDY_HOURS_PER_DAY=4
```

### Getting your Canvas token

1. Log into Canvas
2. Click your profile picture, then go to Account, then Settings
3. Scroll down to Approved Integrations
4. Click New Access Token, give it a name, and copy the token immediately — Canvas only shows it once

---

## Running the planner

```bash
python main.py
```

The agents will work through your assignments and print a complete study plan to the terminal. It takes a few minutes since it makes multiple API calls to Canvas and OpenAI.

---


## Project structure

```
agenta/
├── main.py                  -- run this to generate a study plan
├── .env.example             -- environment variable template
├── requirements.txt
├── agents/
│   └── crew_agents.py       -- the six agent definitions
├── tasks/
│   └── crew_tasks.py        -- the six task definitions
├── tools/
│   └── canvas_tool.py       -- Canvas API tools
└── output/                  -- generated study plans go here
```

---

## Customization

**Change the semester** — update `CANVAS_TERM` in your `.env` at the start of each semester. The value needs to match the term name exactly as it appears in Canvas.

**Adjust your daily limit** — change `MAX_STUDY_HOURS_PER_DAY` to whatever fits your schedule.

**Extend the planning window** — `PLANNING_HORIZON_DAYS` controls how far ahead the planner looks. Default is 14 days.

**Switch to Ollama** — if you want to run everything locally without OpenAI, install Ollama, pull a model, and swap the LLM configuration in `agents/crew_agents.py`. Models like Qwen3 14B or Llama 3.1 8B work well for this kind of task.

---

## Privacy

Everything runs locally. Your Canvas token, assignment data, and generated study plans are never sent to any third-party service other than OpenAI for the LLM inference — and even that can be replaced with a local Ollama model if you prefer complete privacy.

---

## Built with

- CrewAI
- Canvas LMS REST API
- OpenAI / Ollama
