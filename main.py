import os
from dotenv import load_dotenv

load_dotenv()

# Validate env vars before importing anything else
missing = []
for var in ["CANVAS_BASE_URL", "CANVAS_API_TOKEN", "OPENAI_API_KEY"]:
    if not os.getenv(var) or os.getenv(var, "").startswith("your_"):
        missing.append(var)

if missing:
    print("\n❌  Missing required environment variables:")
    for v in missing:
        print(f"   - {v}")
    print("\n👉  Open your .env file and fill in the missing values.\n")
    exit(1)

from crewai import Crew, Process
from agents.crew_agents import (
    canvas_fetcher,
    assignment_summarizer,
    priority_ranker,
    conflict_detector,
    study_planner,
    reminder_scheduler,
)
from tasks.crew_tasks import (
    task_fetch_data,
    task_summarize,
    task_prioritize,
    task_detect_conflicts,
    task_plan,
    task_export,
)


def run():
    print("\n" + "="*60)
    print("AgentA — Canvas Study Planner")
    print("="*60 + "\n")

    crew = Crew(
        agents=[
            canvas_fetcher,
            assignment_summarizer,
            priority_ranker,
            conflict_detector,
            study_planner,
            reminder_scheduler,
        ],
        tasks=[
            task_fetch_data,
            task_summarize,
            task_prioritize,
            task_detect_conflicts,
            task_plan,
            task_export,
        ],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    print("\n" + "="*60)
    print("AgentA finished!")
    print("="*60)


if __name__ == "__main__":
    run()