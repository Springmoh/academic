#!/usr/bin/env python3
"""Check registered/available courses in the saved UTM portal HTML page.

This script parses the local portal HTML copy and prints the course list from the
registration table. It can also check whether a specific course code or name is
present in that table.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Define the target course to check here.
# This may be either a course code like "SKEM4313" or a course name.
COURSE_QUERY = "SKEM4313"
HTML_FILE = Path("studentportal.utm.my/courseRegistration")


def parse_registered_courses(html: str) -> List[Dict[str, str]]:
    courses: List[Dict[str, str]] = []
    pattern = r'<input[^>]+class=["\'][^"\']*cbCourseCode[^"\']*["\'][^>]+value=["\']([^"\']+)["\']'
    for raw in re.findall(pattern, html, re.IGNORECASE):
        parts = [part.strip() for part in raw.split('||')]
        if len(parts) >= 3:
            courses.append({'code': parts[0], 'name': parts[1], 'credit': parts[2]})
    return courses


def find_course(courses: List[Dict[str, str]], query: str) -> Optional[Dict[str, str]]:
    query_lower = query.strip().lower()
    for course in courses:
        if course['code'].lower() == query_lower or course['name'].strip().lower() == query_lower:
            return course
    for course in courses:
        if query_lower in course['name'].lower() or query_lower in course['code'].lower():
            return course
    return None


def main() -> int:
    if not HTML_FILE.exists():
        print(f'Error: HTML file does not exist: {HTML_FILE}', file=sys.stderr)
        return 1

    html = HTML_FILE.read_text(encoding='utf-8', errors='ignore')
    courses = parse_registered_courses(html)
    if not courses:
        print('No registered/available courses found in the HTML file.')
        return 1

    print('Parsed courses:')
    for course in courses:
        print(f"  {course['code']} - {course['name']} ({course['credit']})")

    print()
    print(f'Checking for course query: {COURSE_QUERY}')
    matched = find_course(courses, COURSE_QUERY)
    if matched:
        print('Course found:')
        print(f"  {matched['code']} - {matched['name']} ({matched['credit']})")
        return 0

    print('Course not found in the current registration list.')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
