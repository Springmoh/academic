"""Shared helpers: config loading and parsing of the saved UTM portal page.

All scripts read settings from config.json (copy config.example.json to start)
and parse the locally saved Course Registration page given by "htmlFile".
"""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
CONFIG_EXAMPLE_FILE = SCRIPT_DIR / "config.example.json"

# Matches the course checkboxes, e.g. value="SKEM4313||PLC AND SCADA SYSTEM DESIGN||3"
COURSE_CHECKBOX_PATTERN = r'<input[^>]+class=["\'][^"\']*cbCourseCode[^"\']*["\'][^>]+value=["\']([^"\']+)["\']'

# Hidden fields the portal JavaScript sends with every registration request.
HIDDEN_FIELD_PATTERNS = {
    'csrfToken': r'<meta[^>]+name=["\']csrf-token["\'][^>]+content=["\']([^"\']+)["\']',
    'katPelajar': r'<input[^>]+(?:id=["\']katPelajarId["\']|name=["\']katPelajar["\'])[^>]+value=["\']([^"\']*)["\']',
    'sesisem': r'<input[^>]+(?:id=["\'](?:inputSesisem|sesisemId)["\']|name=["\']sesisem["\'])[^>]+value=["\']([^"\']*)["\']',
    'nokp': r'<input[^>]+(?:id=["\'](?:inputNokp|nokpId)["\']|name=["\']nokp["\'])[^>]+value=["\']([^"\']*)["\']',
}


def loadConfig() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        print(f'Error: {CONFIG_FILE.name} not found. Copy {CONFIG_EXAMPLE_FILE.name} to '
              f'{CONFIG_FILE.name} and fill it in.', file=sys.stderr)
        raise SystemExit(1)
    with CONFIG_FILE.open(encoding='utf-8') as configHandle:
        return json.load(configHandle)


def resolveHtmlFile(config: Dict[str, Any]) -> Path:
    htmlFile = Path(config.get('htmlFile', 'savedPage/courseRegistration.html'))
    return htmlFile if htmlFile.is_absolute() else SCRIPT_DIR / htmlFile


def readHtml(htmlFile: Path) -> str:
    if not htmlFile.exists():
        print(f'Error: HTML file does not exist: {htmlFile}', file=sys.stderr)
        print('Save the portal Course Registration page there first (see README.md).', file=sys.stderr)
        raise SystemExit(1)
    return htmlFile.read_text(encoding='utf-8', errors='ignore')


def parseCourseValue(rawValue: str) -> Optional[Dict[str, str]]:
    parts = [part.strip() for part in rawValue.split('||')]
    if len(parts) < 3:
        return None
    return {'code': parts[0], 'name': parts[1], 'credit': parts[2]}


def parseCourses(html: str) -> List[Dict[str, str]]:
    courses: List[Dict[str, str]] = []
    for rawValue in re.findall(COURSE_CHECKBOX_PATTERN, html, re.IGNORECASE):
        course = parseCourseValue(rawValue)
        if course:
            courses.append(course)
    return courses


def parseHiddenInputs(html: str) -> Dict[str, str]:
    hiddenFields: Dict[str, str] = {}
    for key, pattern in HIDDEN_FIELD_PATTERNS.items():
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            hiddenFields[key] = unescape(match.group(1).strip())
    return hiddenFields


def findCourse(courses: List[Dict[str, str]], query: str) -> Optional[Dict[str, str]]:
    """Exact code match, then exact name match, then a unique substring match."""
    queryLower = query.strip().lower()
    for course in courses:
        if course['code'].lower() == queryLower:
            return course
    for course in courses:
        if course['name'].lower() == queryLower:
            return course
    matches = [course for course in courses
               if queryLower in course['code'].lower() or queryLower in course['name'].lower()]
    if len(matches) == 1:
        return matches[0]
    if matches:
        print('Multiple matching courses found:')
        for course in matches:
            print(f"  {course['code']} - {course['name']} ({course['credit']})")
    return None


def getCourseQuery(config: Dict[str, Any]) -> str:
    """A course passed on the command line overrides "courseQuery" in config.json."""
    return sys.argv[1] if len(sys.argv) > 1 else str(config.get('courseQuery', ''))
