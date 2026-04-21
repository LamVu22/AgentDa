import os
import re
import requests
from datetime import datetime, timezone
from crewai.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CANVAS_BASE_URL", "").rstrip("/")
TOKEN = os.getenv("CANVAS_API_TOKEN", "")
TERM = os.getenv("CANVAS_TERM", "Spring Semester 2026")


def _headers() -> dict:
    return {"Authorization": f"Bearer {TOKEN}"}


def _get_all_pages(url: str, params: dict = None) -> list:
    items = []
    while url:
        resp = requests.get(url, headers=_headers(), params=params, timeout=30)
        resp.raise_for_status()
        items.extend(resp.json())
        params = None
        url = resp.links.get("next", {}).get("url")
    return items


def _format_due_date(due_at: str | None) -> str:
    if not due_at:
        return "No due date"
    dt_utc = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
    dt_local = dt_utc.astimezone()
    return dt_local.strftime("%A, %B %d %Y at %I:%M %p %Z")


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text)  # collapse extra whitespace
    return text.strip()


def _get_submission_state_from_assignment(assignment: dict) -> str:
    submission = assignment.get("submission") or {}
    return submission.get("workflow_state", "unknown")


# ── Tool 1: Fetch enrolled courses for current term ────────────────────────────
class FetchEnrolledCoursesTool(BaseTool):
    name: str = "fetch_enrolled_courses"
    description: str = (
        f"Fetches all courses the student is enrolled in for {TERM} "
        f"from Canvas LMS. Returns course IDs, names, and codes."
    )

    def _run(self) -> str:
        url = f"{BASE_URL}/api/v1/courses"
        params = {
            "enrollment_type": "student",
            "enrollment_state": "active",
            "include[]": "term",
            "per_page": 100,
        }
        resp = requests.get(url, headers=_headers(), params=params, timeout=30)
        if resp.status_code != 200:
            return f"Error fetching courses: {resp.status_code} {resp.text}"

        courses = resp.json()
        spring_courses = [
            c for c in courses
            if (c.get("term") or {}).get("name") == TERM
        ]

        if not spring_courses:
            return f"No courses found for term: {TERM}"

        lines = [f"# Enrolled Courses — {TERM}\n"]
        for c in spring_courses:
            lines.append(
                f"- ID: {c['id']} | {c.get('course_code', '?')} — {c.get('name', 'Unnamed')}"
            )
        return "\n".join(lines)


# ── Tool 2: Fetch unsubmitted upcoming assignments for a course ────────────────
class FetchAssignmentsTool(BaseTool):
    name: str = "fetch_assignments"
    description: str = (
        "Given a Canvas course_id, fetches all upcoming unsubmitted assignments "
        "including name, due date, point value, and description. "
        "Input should be the numeric course_id as a string."
    )

    def _run(self, course_id: str) -> str:
        course_id_int = int(course_id.strip())

        response = requests.get(
            f"{BASE_URL}/api/v1/courses/{course_id_int}",
            headers=_headers(),
            timeout=30
        )
        course_name = response.json().get("name", f"Course {course_id_int}") if response.status_code == 200 else f"Course {course_id_int}"

        assignments = _get_all_pages(
            f"{BASE_URL}/api/v1/courses/{course_id_int}/assignments",
            params={
                "per_page": 100,
                "include[]": "submission",
            },
        )

        if not assignments:
            return f"No assignments found for course {course_id_int}."

        now = datetime.now(timezone.utc)

        # Filter 1: only upcoming
        upcoming = [
            a for a in assignments
            if a.get("due_at") is None
            or datetime.fromisoformat(a["due_at"].replace("Z", "+00:00")) > now
        ]

        # Filter 2: only unsubmitted
        unsubmitted = [
            a for a in upcoming
            if _get_submission_state_from_assignment(a)
            not in ("submitted", "graded", "pending_review")
        ]

        if not unsubmitted:
            return f"No unsubmitted upcoming assignments for {course_name}. ✅ All caught up!"

        lines = [f"# Unsubmitted Upcoming Assignments - {course_name}\n"]
        for a in unsubmitted:
            due_raw = a.get("due_at")
            if due_raw:
                due_dt = datetime.fromisoformat(due_raw.replace("Z", "+00:00"))
                days_left = (due_dt - now).days
                urgency = (
                    "🔴 DUE SOON" if days_left <= 2
                    else "🟡 THIS WEEK" if days_left <= 7
                    else "🟢 UPCOMING"
                )
            else:
                days_left = 9999
                urgency = "⚪ NO DUE DATE"

            desc = _strip_html(a.get("description") or "No description provided.")

            lines.append(f"""
## {a.get('name', 'Untitled')}  {urgency}
- **Due:**    {_format_due_date(due_raw)}
- **Days left:** {days_left if days_left != 9999 else 'N/A'}
- **Points:** {a.get('points_possible', '?')}
- **Submission type:** {', '.join(a.get('submission_types') or ['unknown'])}
- **Description:** {desc}
""")
        return "\n".join(lines)


# ── Tool 3: Get current date ───────────────────────────────────────────────────
class GetCurrentDateTool(BaseTool):
    name: str = "get_current_date"
    description: str = "Returns today's current date and time."

    def _run(self) -> str:
        now = datetime.now()
        return (
            f"Today is {now.strftime('%A, %B %d, %Y')}. "
            f"Current time: {now.strftime('%I:%M %p')}."
        )