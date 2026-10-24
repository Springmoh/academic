#!/usr/bin/env python3
"""Report the status badge of each course row on the saved Course Registration page.

If a table row has no status badge (true for the plain registration table), the
status is reported as UNKNOWN. Checks "courseQuery" from config.json, or a course
code/name given on the command line. Offline only.

Usage:
    python checkCourseRegistrationStatus.py [COURSE_CODE_OR_NAME]
"""

from __future__ import annotations

import re
from typing import Dict, List

from portalCommon import (COURSE_CHECKBOX_PATTERN, findCourse, getCourseQuery, loadConfig,
                          parseCourseValue, readHtml, resolveHtmlFile)

ROW_PATTERN = r'<tr[^>]*>.*?</tr>'
BADGE_PATTERN = r'<span[^>]+class=["\'][^"\']*badge[^"\']*["\'][^>]*>([^<]+)</span>'


def parseRegistrationStatusRows(html: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    # Work row by row so each badge is tied to the course in the same row.
    for rowBlock in re.findall(ROW_PATTERN, html, re.DOTALL | re.IGNORECASE):
        checkboxMatch = re.search(COURSE_CHECKBOX_PATTERN, rowBlock, re.IGNORECASE)
        if not checkboxMatch:
            continue
        course = parseCourseValue(checkboxMatch.group(1))
        if not course:
            continue
        statusMatch = re.search(BADGE_PATTERN, rowBlock, re.IGNORECASE)
        course['status'] = statusMatch.group(1).strip() if statusMatch else 'UNKNOWN'
        rows.append(course)
    return rows


def main() -> int:
    config = loadConfig()
    courseQuery = getCourseQuery(config)
    courses = parseRegistrationStatusRows(readHtml(resolveHtmlFile(config)))
    if not courses:
        print('No registration rows with course checkboxes found in the HTML file.')
        return 1

    print('Parsed course registration rows:')
    for course in courses:
        print(f"  {course['code']} - {course['name']} -> {course['status']}")

    print()
    found = findCourse(courses, courseQuery)
    if found:
        print('Matched course:')
        print(f"  {found['code']} - {found['name']} -> {found['status']}")
        return 0

    print(f'Course not found for query: {courseQuery}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
