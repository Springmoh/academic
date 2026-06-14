#!/usr/bin/env python3
"""Check course registration status from the saved UTM portal HTML.

This script parses the local portal HTML copy and reports status badges
for courses found in the registration/submit tables.

If the page does not contain explicit status badges, the script will still
report the course rows it can parse and mark the status as unknown.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Define the course to check and the HTML file to scan.
COURSE_QUERY = "SKEE4542"
HTML_FILE = Path("studentportal.utm.my/courseRegistration")


def parse_registration_status_rows(html: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    # Split the HTML into table rows to capture row-specific badge text.
    row_blocks = re.findall(r'<tr[^>]*>.*?</tr>', html, re.DOTALL | re.IGNORECASE)
    for block in row_blocks:
        match = re.search(r'<input[^>]+class=["\'][^"\']*cbCourseCode[^"\']*["\'][^>]+value=["\']([^"\']+)["\']', block, re.IGNORECASE)
        if not match:
            continue

        value = match.group(1).strip()
        parts = [part.strip() for part in value.split('||')]
        if len(parts) < 2:
            continue

        code, name = parts[0], parts[1]
        status_match = re.search(r'<span[^>]+class=["\'][^"\']*badge[^"\']*["\'][^>]*>([^<]+)</span>', block, re.IGNORECASE)
        status = status_match.group(1).strip() if status_match else 'UNKNOWN'

        rows.append({'code': code, 'name': name, 'status': status})
    return rows


def find_course_status(courses: List[Dict[str, str]], query: str) -> Optional[Dict[str, str]]:
    q_lower = query.strip().lower()
    for course in courses:
        if course['code'].lower() == q_lower or course['name'].lower() == q_lower:
            return course
    for course in courses:
        if q_lower in course['code'].lower() or q_lower in course['name'].lower():
            return course
    return None


def main() -> int:
    if not HTML_FILE.exists():
        print(f'Error: HTML file does not exist: {HTML_FILE}', file=sys.stderr)
        return 1

    html = HTML_FILE.read_text(encoding='utf-8', errors='ignore')
    courses = parse_registration_status_rows(html)

    if not courses:
        print('No registration rows with course checkboxes found in the HTML file.')
        return 1

    print('Parsed course registration rows:')
    for course in courses:
        print(f"  {course['code']} - {course['name']} -> {course['status']}")

    print()
    found = find_course_status(courses, COURSE_QUERY)
    if found:
        print('Matched course:')
        print(f"  {found['code']} - {found['name']} -> {found['status']}")
        return 0

    print(f'Course not found for query: {COURSE_QUERY}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
