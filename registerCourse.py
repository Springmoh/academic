#!/usr/bin/env python3
"""Automate UTM student portal course registration for one course.

Reads the saved Course Registration page to get the CSRF token, session/student
identifiers (sesisem, nokp, katPelajar) and the course list, then replays the
same requests the page JavaScript makes:

  1. GET  viewSectionDetail      -> list of sections for the course
  2. POST saveDraftStdNew        -> save the chosen course + section as a draft
  3. POST getSubmitRegistration  -> submit the registration (only if "autoSubmit")

Settings (courseQuery, sectionChoice, cookieString, dryRun, autoSubmit, ...)
come from config.json. The cookies and the saved page must come from the same
login session, otherwise the CSRF token is rejected.

Usage:
    python registerCourse.py [COURSE_CODE_OR_NAME]
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlencode

from portalCommon import (SCRIPT_DIR, findCourse, getCourseQuery, loadConfig, parseCourses,
                          parseHiddenInputs, readHtml, resolveHtmlFile)

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore

DEFAULT_BASE_URL = "https://studentportal.utm.my/courseRegistration"
DEBUG_RESPONSE_FILE = SCRIPT_DIR / "debugViewSectionDetailResponse.html"
REQUIRED_HIDDEN_FIELDS = ('katPelajar', 'sesisem', 'nokp')


def parseCookieString(cookieString: str) -> Dict[str, str]:
    cookies: Dict[str, str] = {}
    for item in cookieString.split(';'):
        if '=' in item:
            name, value = item.strip().split('=', 1)
            cookies[name.strip()] = value.strip()
    return cookies


def buildSession(cookieString: str, baseUrl: str) -> Any:
    if requests is None:
        raise RuntimeError('requests library is required. Install with `pip install -r requirements.txt`.')
    session = requests.Session()
    session.cookies.update(parseCookieString(cookieString))
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": baseUrl,
        "Origin": "https://studentportal.utm.my",
    })
    return session


def parseJsonResponse(response: Any) -> Any:
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return {'text': response.text}


def callViewSectionDetail(session: Any, baseUrl: str, courseCode: str) -> Dict[str, Any]:
    url = f"{baseUrl.rstrip('/')}/viewSectionDetail?courseCode_token={quote_plus(courseCode)}"
    response = session.get(url, allow_redirects=False)

    print("\n--- DEBUG viewSectionDetail ---")
    print("Request URL:", url)
    print("Status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Location:", response.headers.get("Location"))
    print("First 1000 chars:")
    print(response.text[:1000])
    print("--- END DEBUG ---\n")

    # Keep the full response for troubleshooting (e.g. a login page means expired cookies).
    DEBUG_RESPONSE_FILE.write_text(response.text, encoding="utf-8", errors="ignore")

    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        raise RuntimeError(
            f"Server did not return JSON. Full response saved as {DEBUG_RESPONSE_FILE.name}"
        )


def selectSection(sectionList: List[Dict[str, Any]], desiredSection: Optional[str] = None) -> Optional[str]:
    """Return the desired section if it is not full, or the first non-full section when none is given."""
    desiredSectionNormalized = desiredSection.strip().lower() if desiredSection else None
    for section in sectionList:
        limitStatus = str(section.get('limit_status', '')).strip().lower()
        sectionId = str(section.get('jas_seksyem') or '').strip()
        if limitStatus == 'full' or not sectionId:
            continue
        if desiredSectionNormalized is None or sectionId.lower() == desiredSectionNormalized:
            return sectionId
    return None


def saveDraft(session: Any, baseUrl: str, selections: List[Dict[str, str]],
              csrfToken: Optional[str] = None) -> Any:
    """Mirror the page's saveDraftStdNew call.

    `selections` is a list of objects with keys:
      code, subject, credit, section, sesisem, nokp, katPelajar
    """
    url = f"{baseUrl.rstrip('/')}/saveDraftStdNew"
    headers = {'X-CSRF-TOKEN': csrfToken} if csrfToken else {}
    response = session.post(url, json={'checkboxElemsRecord': selections}, headers=headers)
    return parseJsonResponse(response)


def submitRegistration(session: Any, baseUrl: str, sesisem: str, nokp: str, proses: str = 'add',
                       katPelajar: Optional[str] = None, noKerjaPA: str = '', kodProses: str = '',
                       remarkStudent: str = '', csrfToken: Optional[str] = None) -> Any:
    """Mirror the page's getSubmitRegistration call (POST with query parameters)."""
    params = {
        'sesisem_token': sesisem,
        'nokp_token': nokp,
        'proses_token': proses,
        'katPelajar_token': katPelajar or '',
        'noKerjaPA_token': noKerjaPA,
        'kodProses_token': kodProses,
        'remarkStudent_token': remarkStudent,
    }
    url = f"{baseUrl.rstrip('/')}/getSubmitRegistration?" + urlencode(params)
    headers = {'X-CSRF-TOKEN': csrfToken} if csrfToken else {}
    response = session.post(url, headers=headers)
    return parseJsonResponse(response)


def main() -> int:
    config = loadConfig()
    courseQuery = getCourseQuery(config)
    sectionChoice = config.get('sectionChoice') or None
    cookieString = str(config.get('cookieString', ''))
    baseUrl = str(config.get('baseUrl') or DEFAULT_BASE_URL)
    dryRun = bool(config.get('dryRun', False))
    autoSubmit = bool(config.get('autoSubmit', False))

    html = readHtml(resolveHtmlFile(config))
    hiddenFields = parseHiddenInputs(html)
    courses = parseCourses(html)

    if not courses:
        print('Error: no courses found in the HTML file.', file=sys.stderr)
        return 1

    course = findCourse(courses, courseQuery)
    if course is None:
        print(f'Course not found for query: {courseQuery}', file=sys.stderr)
        print('Available courses:')
        for item in courses:
            print(f"  {item['code']} - {item['name']} ({item['credit']})")
        return 1

    print(f"Selected course: {course['code']} - {course['name']} ({course['credit']})")

    for requiredField in REQUIRED_HIDDEN_FIELDS:
        if not hiddenFields.get(requiredField):
            print(f'Error: missing hidden field {requiredField} in HTML file.', file=sys.stderr)
            return 1

    if dryRun:
        print('Dry run complete. No network request made.')
        return 0

    if requests is None:
        print('Error: requests library is required. Install with `pip install -r requirements.txt`.',
              file=sys.stderr)
        return 1

    if not cookieString or 'PASTE_HERE' in cookieString:
        print('Error: set "cookieString" in config.json (see README.md).', file=sys.stderr)
        return 1

    csrfToken = hiddenFields.get('csrfToken')
    session = buildSession(cookieString, baseUrl)
    if csrfToken:
        session.headers['X-CSRF-TOKEN'] = csrfToken

    print('Fetching section list...')
    sectionData = callViewSectionDetail(session, baseUrl, course['code'])
    sectionList = sectionData.get('getSectionList') or sectionData.get('sectionList') or []
    if not sectionList:
        print('Error: no section list returned from viewSectionDetail request.', file=sys.stderr)
        print('Response data:', json.dumps(sectionData, indent=2))
        return 1

    section = selectSection(sectionList, sectionChoice)
    if section is None:
        choiceMessage = f' for sectionChoice={sectionChoice}' if sectionChoice else ''
        print(f'Error: no available section found{choiceMessage} for this course.', file=sys.stderr)
        print('Section list returned:')
        print(json.dumps(sectionList, indent=2))
        return 1

    print(f'Selected section: {section}')
    # Mirrors one checkboxElemsRecord entry built by the page JavaScript.
    selection = {
        'code': course['code'],
        'subject': course['name'],
        'credit': course['credit'],
        'section': section,
        'sesisem': hiddenFields['sesisem'],
        'nokp': hiddenFields['nokp'],
        'katPelajar': hiddenFields['katPelajar'],
    }

    print('Saving draft for selection...')
    draftResponse = saveDraft(session, baseUrl, [selection], csrfToken)
    print('Draft response:')
    print(json.dumps(draftResponse, indent=2, ensure_ascii=False))

    if autoSubmit:
        print('Auto-submit enabled — submitting registration...')
        submitResponse = submitRegistration(
            session,
            baseUrl,
            sesisem=hiddenFields['sesisem'],
            nokp=hiddenFields['nokp'],
            proses='add',
            katPelajar=hiddenFields.get('katPelajar'),
            csrfToken=csrfToken,
        )
        print('Submit response:')
        print(json.dumps(submitResponse, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
