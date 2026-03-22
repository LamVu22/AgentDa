import os
from crewai import Task
from dotenv import load_dotenv
from agents.crew_agents import (
    canvas_fetcher,
    assignment_summarizer,
    priority_ranker,
    conflict_detector,
    study_planner,
    reminder_scheduler,
)

load_dotenv()

PLANNING_DAYS = os.getenv("PLANNING_HORIZON_DAYS", "14")
MAX_HOURS = os.getenv("MAX_STUDY_HOURS_PER_DAY", "4")


task_fetch_data = Task(
    description=(
        "1. Use the fetch_enrolled_courses tool to get all active courses.\n"
        "2. For each course returned, use the fetch_assignments tool with "
        "that course's ID to get all upcoming assignments.\n"
        "3. Compile everything into a single structured dataset."
    ),
    expected_output=(
        "A complete list of all enrolled courses and their upcoming assignments "
        "including: assignment name, due date, point value, submission type, "
        "and description."
    ),
    agent=canvas_fetcher,
)

task_summarize = Task(
    description=(
        "Review the raw Canvas assignment data from the previous task.\n"
        "For each assignment:\n"
        "- Write a 2-3 sentence plain-English summary of what the student must do.\n"
        "- Note the due date and points clearly.\n"
        "- Estimate complexity: LOW (under 1 hr), MEDIUM (1-4 hrs), HIGH (4+ hrs).\n"
        "- Flag any assignment with a vague or missing description with ⚠️ CHECK CANVAS."
    ),
    expected_output=(
        "A formatted list of all assignments with: plain-English summary, "
        "due date, point value, complexity estimate, and any ⚠️ flags."
    ),
    agent=assignment_summarizer,
    context=[task_fetch_data],
)

task_prioritize = Task(
    description=(
        "Using the summarized assignments, rank them by priority.\n"
        "Use these urgency levels:\n"
        "- CRITICAL: due within 3 days\n"
        "- HIGH: due within 7 days\n"
        "- MEDIUM: due within 14 days\n"
        "- LOW: beyond 14 days\n"
        "Factor in point value and complexity alongside urgency.\n"
        "Output a numbered list from most to least urgent."
    ),
    expected_output=(
        "A numbered priority list of all assignments showing: rank, name, "
        "course, due date, priority level, and a one-line rationale."
    ),
    agent=priority_ranker,
    context=[task_summarize],
)

task_detect_conflicts = Task(
    description=(
        "Analyze all assignment due dates and identify:\n"
        "1. Days where 2 or more assignments are due simultaneously.\n"
        "2. Weeks with 3 or more deadlines.\n"
        "3. For each conflict, recommend which assignment to start early "
        "and by how many days, with a clear reason why."
    ),
    expected_output=(
        "A conflict report listing all deadline collisions, heavy weeks, "
        "and specific start-early recommendations with reasoning."
    ),
    agent=conflict_detector,
    context=[task_summarize],
)

task_plan = Task(
    description=(
        f"Use the get_current_date tool to confirm today's date.\n"
        f"Then using the priority ranking, conflict report, and assignment "
        f"summaries, create a day-by-day study plan for the next {PLANNING_DAYS} days.\n\n"
        f"Rules:\n"
        f"- Max {MAX_HOURS} study hours per day.\n"
        f"- Always leave a 1-day buffer before each deadline.\n"
        f"- Break HIGH complexity assignments into multiple sessions.\n"
        f"- Group LOW complexity tasks together when possible.\n"
        f"- Format each day as:\n"
        f"  [Date] → [Assignment] — [Session goal] — [Est. time]"
    ),
    expected_output=(
        "A detailed day-by-day study plan for the next planning horizon. "
        "Each day lists assignments to work on, the session goal, and "
        "estimated time. Includes a summary of total weekly study hours."
    ),
    agent=study_planner,
    context=[task_summarize, task_prioritize, task_detect_conflicts],
)

task_export = Task(
    description=(
        "Take the study plan and produce a clean weekly checklist.\n"
        "Group assignments by week.\n"
        "Each item should have a [ ] checkbox, the assignment name, "
        "course, due date, and estimated time.\n"
        "Add a header for each week like: === Week of [date] ==="
    ),
    expected_output=(
        "A complete plain-text weekly checklist of all assignments "
        "grouped by week with [ ] checkboxes, ready to print or save."
    ),
    agent=reminder_scheduler,
    context=[task_plan],
)