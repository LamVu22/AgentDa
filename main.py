import os
from datetime import datetime
from pathlib import Path
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

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%m-%d-%Y")
    output_path = output_dir / f"study_plan_{timestamp}.txt"
    output_path.write_text(str(result), encoding="utf-8")

    print("\n" + "="*60)
    print("Finished running!")
    print(f"You can find your plan at: {output_path}")
    print("="*60)


if __name__ == "__main__":
    run()