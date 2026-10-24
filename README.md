# earlyCourseReg

Small Python tool that registers a course on the **UTM Student Portal**
(`https://studentportal.utm.my/courseRegistration`) the moment registration opens,
without clicking through the web UI.

It does **not** log in for you. Instead it:

1. Reads a copy of the **Course Registration** page that you save from your browser
   (to get the CSRF token, your session/student identifiers and the course list).
2. Re-uses your browser's **session cookies** to call the same endpoints the page's
   JavaScript calls:
   - `GET  viewSectionDetail` – list the sections of the chosen course
   - `POST saveDraftStdNew` – save course + section as a draft
   - `POST getSubmitRegistration` – submit the registration (only when `autoSubmit` is `true`)

## Project layout

| File | Purpose |
| --- | --- |
| `registerCourse.py` | Main script: picks the course and section, saves the draft, optionally submits. |
| `checkRegisteredCourse.py` | Offline: lists the courses in the saved page's registration table and checks one course. |
| `checkCourseRegistrationStatus.py` | Offline: shows the status badge per course row (`UNKNOWN` if the page has none). |
| `portalCommon.py` | Shared code: loads `config.json` and parses the saved page. |
| `config.example.json` | Config template (committed). |
| `config.json` | Your real config, including cookies (**git-ignored**). |
| `savedPage/courseRegistration.html` | The page you save from the portal (**git-ignored**: it contains your IC number and CSRF token). |
| `requirements.txt` | Python dependencies (`requests`). |

## One-time setup

```bash
cd earlyCourseReg
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy config.example.json config.json   # macOS/Linux: cp config.example.json config.json
```

## Each registration (do these steps in this order, in one login session)

The cookies and the saved page **must come from the same login session**. The
CSRF token inside the page belongs to that session. If you log in again, repeat steps 1–2.

### 1. Save the Course Registration page

1. Log in to the Student Portal and open **Course Registration** (the page that lists
   courses with checkboxes and "Add Section" buttons).
2. Press `Ctrl+S` and choose **Webpage, HTML Only** (or *Complete*, the extra
   `_files` folder isn't needed).
3. Save it as `savedPage/courseRegistration.html`, replacing the old file.
   You can use another path if you set `"htmlFile"` in `config.json` to it.

Check that the page was parsed:

```bash
python checkRegisteredCourse.py
```

You should see the course list for the current session.

### 2. Copy your session cookies

1. On the same portal tab press `F12` → **Network** tab → reload the page (`F5`).
2. Click the `courseRegistration` request → **Headers** → **Request Headers** → `Cookie`.
3. Copy the `XSRF-TOKEN=...; student_session=...` part into `"cookieString"` in `config.json`.
   (Alternative: **Application** → **Cookies** → `https://studentportal.utm.my`, copy both values.)

### 3. Edit `config.json`

```json
{
  "htmlFile": "savedPage/courseRegistration.html",
  "baseUrl": "https://studentportal.utm.my/courseRegistration",
  "courseQuery": "SKEM4313",
  "sectionChoice": "01",
  "cookieString": "XSRF-TOKEN=...; student_session=...",
  "dryRun": true,
  "autoSubmit": false
}
```

| Key | Meaning |
| --- | --- |
| `htmlFile` | Saved page path, relative to this folder (or absolute). |
| `baseUrl` | Portal registration URL. Only change it if the portal URL changes. |
| `courseQuery` | Course **code** (`SKEM4313`) or **name**. Partial text works if only one course matches. A command-line argument overrides it. |
| `sectionChoice` | Section ID exactly as the portal shows it (e.g. `"01"`). Use `null` to take the first section that isn't full. If the chosen section is full the script stops and does not pick another one. |
| `cookieString` | Cookies from step 2. |
| `dryRun` | `true` only parses the saved page and checks the course and hidden fields. Nothing is sent. |
| `autoSubmit` | `false` only saves a **draft** (you then press Submit in the portal). `true` also submits the registration. |

### 4. Run

```bash
python registerCourse.py              # uses courseQuery from config.json
python registerCourse.py SKEE4542     # override the course for this run
```

Recommended order: run with `"dryRun": true`, then set it to `false` and run again.
Then check the result in the portal. Set `"autoSubmit": true` only once you trust the draft step.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `config.json not found` | Copy `config.example.json` to `config.json`. |
| `HTML file does not exist` | Save the page to the path in `htmlFile` (step 1). |
| `missing hidden field ...` | Wrong page saved. It must be the Course Registration page itself. |
| `Status: 302` / `Location: .../login`, or `Server did not return JSON` | Cookies expired, or don't match the saved page. Log in again and redo steps 1–2. The full response is saved in `debugViewSectionDetailResponse.html`. |
| `419` error | CSRF token mismatch. The page and cookies come from different sessions. Redo steps 1–2. |
| `no available section found` | `sectionChoice` is full or doesn't exist. The script prints the section list. Choose another section or use `null`. |
| `Multiple matching courses found` | Make `courseQuery` more specific (use the course code). |

## Notes

- `checkCourseRegistrationStatus.py` reads `<span class="badge">` elements in the course rows.
  The normal registration table has none, so it usually prints `UNKNOWN`.
- `checkRegisteredCourse.py` lists the courses **offered for registration** on the saved
  page, not the ones already confirmed.
- Never commit `config.json` or `savedPage/`. They hold your login cookies and personal data.
- Naming convention: file names, functions and local variables use `camelCase`, module-level constants use `UPPER_SNAKE_CASE`.
  Keys sent to the portal (`courseCode_token`, `jas_seksyem`, ...) keep the portal's own spelling.
