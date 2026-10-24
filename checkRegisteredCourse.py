#!/usr/bin/env python3
"""List the courses offered on the saved Course Registration page.

Prints every course in the registration table (the courses with a checkbox you
can register for) and checks whether "courseQuery" from config.json, or a
course code/name given on the command line, is among them. Offline only.

Usage:
    python checkRegisteredCourse.py [COURSE_CODE_OR_NAME]
"""

from __future__ import annotations

from portalCommon import findCourse, getCourseQuery, loadConfig, parseCourses, readHtml, resolveHtmlFile


def main() -> int:
    config = loadConfig()
    courseQuery = getCourseQuery(config)
    courses = parseCourses(readHtml(resolveHtmlFile(config)))
    if not courses:
        print('No registered/available courses found in the HTML file.')
        return 1

    print('Parsed courses:')
    for course in courses:
        print(f"  {course['code']} - {course['name']} ({course['credit']})")

    print()
    print(f'Checking for course query: {courseQuery}')
    matched = findCourse(courses, courseQuery)
    if matched:
        print('Course found:')
        print(f"  {matched['code']} - {matched['name']} ({matched['credit']})")
        return 0

    print('Course not found in the current registration list.')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
