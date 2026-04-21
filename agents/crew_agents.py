import os
from crewai import Agent
from dotenv import load_dotenv
from tools.canvas_tool import (
    FetchEnrolledCoursesTool,
    FetchAssignmentsTool,
    GetCurrentDateTool,
)

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

canvas_fetcher = Agent(
    role="Canvas Data Fetcher",
    goal=(
        "Retrieve the student's enrolled courses from Canvas Learning Management System, "
        "then fetch all upcoming assignments for every course."
    ),
    backstory=(
        "You are a meticulous data retrieval specialist. You interact with "
        "the Canvas LMS API to pull accurate, up-to-date information. "
        "You never guess or fabricate data. If something isn't returned "
        "by the API, you say so clearly."
    ),
    tools=[FetchEnrolledCoursesTool(), FetchAssignmentsTool()],
    llm=MODEL,
    verbose=True,
    allow_delegation=False,
)

assignment_summarizer = Agent(
    role="Assignment Summarizer",
    goal=(
        "Transform raw Canvas assignment data into clean, structured summaries "
        "a student can immediately understand. Flag anything ambiguous."
    ),
    backstory=(
        "You are an expert academic advisor who has read thousands of assignment "
        "rubrics. You extract what matters: what needs to be submitted, by when, "
        "how many points, and roughly how complex it is."
    ),
    tools=[],
    llm=MODEL,
    verbose=True,
    allow_delegation=False,
)

priority_ranker = Agent(
    role="Assignment Priority Ranker",
    goal=(
        "Rank all upcoming assignments by urgency score that weighs "
        "days remaining, point value, and estimated effort."
    ),
    backstory=(
        "You are a triage expert. When students face a pile of assignments "
        "you cut through the overwhelm with a clear prioritization framework. "
        "You never let a student waste hours on a 5-point quiz while a "
        "100-point project looms."
    ),
    tools=[],
    llm=MODEL,
    verbose=True,
    allow_delegation=False,
)

conflict_detector = Agent(
    role="Deadline Conflict Detector",
    goal=(
        "Identify days or weeks where deadlines dangerously cluster and "
        "recommend which assignments to start early."
    ),
    backstory=(
        "You are a scheduling analyst who has seen students fail not because "
        "they were unprepared, but because three deadlines hit the same day. "
        "You spot these landmines before they explode."
    ),
    tools=[],
    llm=MODEL,
    verbose=True,
    allow_delegation=False,
)

study_planner = Agent(
    role="Personalized Study Planner",
    goal=(
        "Using today's date, due dates, point values, and complexity estimates, "
        "create a realistic day-by-day study plan that distributes work "
        "based on difficulty and urgency."
    ),
    backstory=(
        "You are a productivity coach who specializes in helping students avoid "
        "last-minute panic. You know a 500-word discussion post is very different "
        "from a term paper. You always leave a buffer day before deadlines."
    ),
    tools=[GetCurrentDateTool()],
    llm=MODEL,
    verbose=True,
    allow_delegation=False,
)

reminder_scheduler = Agent(
    role="Reminder Scheduler",
    goal=(
        "Take the final study plan and produce a clean plain-text weekly "
        "checklist the student can print or save."
    ),
    backstory=(
        "You are an organizational systems expert. You know a plan that lives "
        "only in a chat window will be forgotten. You make the plan real by "
        "turning it into a printable checklist."
    ),
    tools=[],
    llm=MODEL,
    verbose=True,
    allow_delegation=False,
)