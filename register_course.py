#!/usr/bin/env python3
"""Automate UTM student portal course registration for a specific course name.

This script parses a local copy of the registration page to extract current session
and course data, then submits a registration request using the same endpoint
pattern found in the page JavaScript.

Usage:
  Set COURSE_QUERY, SESSION_COOKIE, and XSRF_COOKIE at the top of this file, then run:
      python register_course.py

The script uses the local HTML copy to extract:
  - CSRF token
  - student category (katPelajar)
  - session / student identifiers (sesisem, nokp)
  - available courses and credits

It then requests available sections and posts the chosen section to addSubject.
"""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlencode

# Define the target course and authenticated cookies here.
# COURSE_QUERY may be either the course code or the full course name.
# To choose a specific section, set SECTION_CHOICE to the desired section code.
# Leave SECTION_CHOICE as None to automatically register the first open section.
COURSE_QUERY = "SKEM4313"
SECTION_CHOICE = "01"  # e.g. "A" or "S01" depending on the portal's section IDs
#COOKIE_STRING = r"""XSRF-TOKEN=PASTE_HERE; student_session=PASTE_HERE"""
COOKIE_STRING = r"""XSRF-TOKEN=eyJpdiI6IlN1THNtNW9ETVNEaU51SDZpYy9vdkE9PSIsInZhbHVlIjoiNXYvcFV1UGdaa3VwQzBIc3UwWGVJUEFtbHV1Y2dseXZhekxxcnVYYzRLYU5DWnZBdjVmdm5kaUFzR3VSWnJsRGpZQXNYTXZhZEVENUlhLzRZT1JEbWZVOWVsektlT1k5QVYwTXE5cC95Qktaa0YrbWMraEgxQm1nTUNnZDgvcDUiLCJtYWMiOiIyZDlhYWRhNmUzOTMyMWQ1MmJlYjcyN2JhYWMzOWMwNDQxM2MzZGIyMWRiNmRlZmE2YTRiYTg1MjZlYzdjZWZiIiwidGFnIjoiIn0%3D; student_session=eyJpdiI6InJvMldlaWN2dVJhcTNmM3pVSGhkYUE9PSIsInZhbHVlIjoienNyVG1rVEV5Y3VyQXRXbVg2cmdwMHpkUU9jV2F3ZTFXellqUWswNVY3TG1sWDFNYnlJdmlYaFFQMktzTWo3QVNJRVljSFpkOXhCUy9vVkM4WWhybGdZNVlZY2RnUUhrU00wcnk4OVZJaDhhQkFhWkRYbzhOWUFpalVKaGwyU0giLCJtYWMiOiIwMzFmMTBiMjFjNDRiMzQ5OGE5YjczMjE0MDYwMmQ3MzNhMDNhZjAwNTNmYjQ2OTc3N2VmN2MyYWYyMjE4Y2IzIiwidGFnIjoiIn0%3D"""
HTML_FILE = Path("studentportal.utm.my/courseRegistration")
BASE_URL = "https://studentportal.utm.my/courseRegistration"

DRY_RUN = False
AUTO_SUBMIT = False  # if True, call getSubmitRegistration after saving draft

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore


def parse_hidden_inputs(html: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    # accept multiple possible id/name variants present in the saved HTML
    patterns = {
        'csrf_token': r'<meta[^>]+name=["\']csrf-token["\'][^>]+content=["\']([^"\']+)["\']',
        'katPelajar': r'<input[^>]+(?:id=["\']katPelajarId["\']|name=["\']katPelajar["\'])[^>]+value=["\']([^"\']*)["\']',
        'sesisem': r'<input[^>]+(?:id=["\'](?:inputSesisem|sesisemId)["\']|name=["\']sesisem["\'])[^>]+value=["\']([^"\']*)["\']',
        'nokp': r'<input[^>]+(?:id=["\'](?:inputNokp|nokpId)["\']|name=["\']nokp["\'])[^>]+value=["\']([^"\']*)["\']',
        'inputCourse': r'<input[^>]+id=["\']inputCourse["\'][^>]+value=["\']([^"\']*)["\']',
        'inputCredit': r'<input[^>]+id=["\']inputCredit["\'][^>]+value=["\']([^"\']*)["\']',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            result[key] = unescape(match.group(1).strip())
    return result


def parse_courses(html: str) -> List[Dict[str, str]]:
    courses: List[Dict[str, str]] = []
    # parse cbCourseCode values like "SKEM4313||PLC AND SCADA SYSTEM DESIGN||3"
    for raw in re.findall(r'<input[^>]+class=["\'][^"\']*cbCourseCode[^"\']*["\'][^>]+value=["\']([^"\']+)["\']', html, re.IGNORECASE):
        parts = [part.strip() for part in raw.split('||')]
        if len(parts) >= 3:
            courses.append({
                'code': parts[0],
                'name': parts[1],
                'credit': parts[2],
            })
    return courses


def choose_course(courses: List[Dict[str, str]], query: str) -> Optional[Dict[str, str]]:
    query_lower = query.strip().lower()
    # exact code match first
    for course in courses:
        if course['code'].lower() == query_lower:
            return course
    # exact name match
    for course in courses:
        if course['name'].strip().lower() == query_lower:
            return course
    # substring search
    matches = [course for course in courses if query_lower in course['name'].lower() or query_lower in course['code'].lower()]
    if len(matches) == 1:
        return matches[0]
    if matches:
        print('Multiple matching courses found:')
        for course in matches:
            print(f"  {course['code']} - {course['name']} ({course['credit']})")
    return None


def parse_cookie_string(cookie_string: str) -> Dict[str, str]:
    cookies: Dict[str, str] = {}
    for item in cookie_string.split(';'):
        if '=' in item:
            name, value = item.strip().split('=', 1)
            cookies[name.strip()] = value.strip()
    return cookies


def build_session(session_cookie: Optional[str], xsrf_cookie: Optional[str]) -> Any:
    if requests is None:
        raise RuntimeError('requests library is required. Install with `pip install requests`.')
    session = requests.Session()
    if session_cookie:
        session.cookies.update(parse_cookie_string(session_cookie))
    if xsrf_cookie:
        session.cookies.update(parse_cookie_string(xsrf_cookie))
    session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://studentportal.utm.my/courseRegistration",
    "Origin": "https://studentportal.utm.my",
    })
    return session


def get_html_from_file(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore')


def call_view_section_detail(session: Any, base_url: str, course_code: str) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/viewSectionDetail?courseCode_token={quote_plus(course_code)}"

    response = session.get(url, allow_redirects=False)

    print("\n--- DEBUG viewSectionDetail ---")
    print("Request URL:", url)
    print("Status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Location:", response.headers.get("Location"))
    print("First 1000 chars:")
    print(response.text[:1000])
    print("--- END DEBUG ---\n")

    # Save full response for checking
    Path("debug_viewSectionDetail_response.html").write_text(
        response.text,
        encoding="utf-8",
        errors="ignore"
    )

    response.raise_for_status()

    try:
        return response.json()
    except ValueError:
        raise RuntimeError(
            "Server did not return JSON. Full response saved as "
            "debug_viewSectionDetail_response.html"
        )


def select_section(section_list: List[Dict[str, Any]], desired_section: Optional[str] = None) -> Optional[str]:
    desired_section_normalized = desired_section.strip().lower() if desired_section else None
    if desired_section_normalized:
        for section in section_list:
            limit_status = str(section.get('limit_status', '')).strip().lower()
            section_id = str(section.get('jas_seksyem') or '').strip()
            if section_id.lower() == desired_section_normalized and limit_status != 'full':
                return section_id
        return None

    for section in section_list:
        limit_status = str(section.get('limit_status', '')).strip().lower()
        if limit_status != 'full':
            selected = str(section.get('jas_seksyem') or '').strip()
            if selected:
                return selected
    return None


def submit_add_subject(
    session: Any,
    base_url: str,
    course_code: str,
    credit: str,
    section: str,
    sesisem: str,
    nokp: str,
    katPelajar: str,
    csrf_token: Optional[str] = None,
) -> Any:
    url = (
        f"{base_url.rstrip('/')}/addSubject?"
        + urlencode({
            'courseCode_token': course_code,
            'courseCredit_token': credit,
            'courseSection_token': section,
            'sesisem_token': sesisem,
            'nokp_token': nokp,
            'katPelajar_token': katPelajar,
        })
    )
    headers = {'X-CSRF-TOKEN': csrf_token} if csrf_token else {}
    response = session.post(url, headers=headers)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return {'text': response.text}


def save_draft(
    session: Any,
    base_url: str,
    selections: List[Dict[str, str]],
    csrf_token: Optional[str] = None,
) -> Any:
    """Mirror the page's saveDraftStdNew call.

    `selections` should be a list of objects with keys:
      code, subject, credit, section, sesisem, nokp, katPelajar
    """
    url = f"{base_url.rstrip('/')}/saveDraftStdNew"
    headers = {'X-CSRF-TOKEN': csrf_token} if csrf_token else {}
    # send JSON payload mirroring the jQuery call on the page
    payload = {'checkboxElemsRecord': selections}
    if DRY_RUN:
        print('DRY RUN: would POST to', url)
        print('Headers:', headers)
        print('Payload:', json.dumps(payload, indent=2, ensure_ascii=False))
        return {'status': 'dry-run'}
    resp = session.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        return {'text': resp.text}


def submit_registration(
    session: Any,
    base_url: str,
    sesisem: str,
    nokp: str,
    proses: str = 'add',
    katPelajar: Optional[str] = None,
    noKerjaPA: str = '',
    kodProses: str = '',
    remarkStudent: str = '',
    csrf_token: Optional[str] = None,
) -> Any:
    """Mirror the page's getSubmitRegistration call.

    The JS issues a POST to `getSubmitRegistration` with query parameters; we do the same.
    """
    params = {
        'sesisem_token': sesisem,
        'nokp_token': nokp,
        'proses_token': proses,
        'katPelajar_token': katPelajar or '',
        'noKerjaPA_token': noKerjaPA,
        'kodProses_token': kodProses,
        'remarkStudent_token': remarkStudent,
    }
    url = f"{base_url.rstrip('/')}/getSubmitRegistration?" + urlencode(params)
    headers = {'X-CSRF-TOKEN': csrf_token} if csrf_token else {}
    if DRY_RUN:
        print('DRY RUN: would POST to', url)
        print('Headers:', headers)
        return {'status': 'dry-run'}
    resp = session.post(url, headers=headers)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        return {'text': resp.text}


def main() -> int:
    html_path = HTML_FILE
    if not html_path.exists():
        print(f'Error: HTML file does not exist: {html_path}', file=sys.stderr)
        return 1

    html = get_html_from_file(html_path)
    hidden = parse_hidden_inputs(html)
    courses = parse_courses(html)

    if not courses:
        print('Error: no courses found in the HTML file.', file=sys.stderr)
        return 1

    course = choose_course(courses, COURSE_QUERY)
    if course is None:
        print(f'Course not found for query: {COURSE_QUERY}', file=sys.stderr)
        print('Available courses:')
        for item in courses:
            print(f"  {item['code']} - {item['name']} ({item['credit']})")
        return 1

    print(f"Selected course: {course['code']} - {course['name']} ({course['credit']})")

    for required in ('katPelajar', 'sesisem', 'nokp'):
        if required not in hidden or not hidden[required]:
            print(f'Error: missing hidden field {required} in HTML file.', file=sys.stderr)
            return 1

    if DRY_RUN:
        print('Dry run complete. No network request made.')
        return 0

    if requests is None:
        print('Error: requests library is required. Install with `pip install requests`.', file=sys.stderr)
        return 1

    session = build_session(COOKIE_STRING, None)
    if hidden.get('csrf_token'):
        session.headers['X-CSRF-TOKEN'] = hidden['csrf_token']

    print('Fetching section list...')
    section_data = call_view_section_detail(session, BASE_URL, course['code'])
    section_list = section_data.get('getSectionList') or section_data.get('sectionList') or []
    if not section_list:
        print('Error: no section list returned from viewSectionDetail request.', file=sys.stderr)
        print('Response data:', json.dumps(section_data, indent=2))
        return 1

    section = select_section(section_list, SECTION_CHOICE)
    if section is None:
        choice_msg = f' for SECTION_CHOICE={SECTION_CHOICE}' if SECTION_CHOICE else ''
        print(f'Error: no available section found{choice_msg} for this course.', file=sys.stderr)
        print('Section list returned:')
        print(json.dumps(section_list, indent=2))
        return 1

    print(f'Selected section: {section}')
    # Build the draft payload (mirrors checkboxElemsRecord entries)
    selection = {
        'code': course['code'],
        'subject': course['name'],
        'credit': course['credit'],
        'section': section,
        'sesisem': hidden['sesisem'],
        'nokp': hidden['nokp'],
        'katPelajar': hidden['katPelajar'],
    }

    print('Saving draft for selection...')
    draft_resp = save_draft(session=session, base_url=BASE_URL, selections=[selection], csrf_token=hidden.get('csrf_token'))
    print('Draft response:')
    print(json.dumps(draft_resp, indent=2, ensure_ascii=False))

    if AUTO_SUBMIT:
        print('Auto-submit enabled — submitting registration...')
        submit_resp = submit_registration(
            session=session,
            base_url=BASE_URL,
            sesisem=hidden['sesisem'],
            nokp=hidden['nokp'],
            proses='add',
            katPelajar=hidden.get('katPelajar'),
            csrf_token=hidden.get('csrf_token'),
        )
        print('Submit response:')
        print(json.dumps(submit_resp, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
