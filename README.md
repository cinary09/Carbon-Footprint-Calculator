# 🌍 Climate Action Tracker

A Flask web app for logging everyday climate-positive actions, scoring
them, and tracking your progress over time.

This version is a **merge** of three independently built drafts of the
same project (one built with ChatGPT, one with Claude, one with
Gemini). Instead of picking a single draft, the strongest piece of
each was kept — see [Merge notes](#merge-notes) below.

---

## Features

- **Accounts** — register with username, email, and password; passwords
  are hashed with Werkzeug's `generate_password_hash` / `check_password_hash`,
  never stored in plain text.
- **Activity logging** — add, edit, and delete climate actions (recycling,
  cycling, public transport, planting trees, saving electricity/water),
  each with a date and optional notes.
- **Points system** — every activity type has a fixed point value; your
  dashboard shows a running total.
- **Statistics page** — total points, total activities, most common
  action, average points per activity, a full per-activity breakdown
  table, and progress bars.
- **Flash messages** — clear feedback after every action (success,
  error, warning), including a personalized welcome-back message on login.
- **Zero JavaScript** — every interaction, including delete confirmation,
  is handled server-side with Flask, Jinja2, and plain HTML forms. There
  is a dedicated confirmation page for deletes instead of a JS `confirm()`
  popup.

---

## Tech stack

| Layer      | Choice                                   |
|------------|-------------------------------------------|
| Backend    | Flask                                      |
| Templating | Jinja2                                     |
| Auth/security | Werkzeug (`werkzeug.security`)          |
| Database   | SQLite (via the standard `sqlite3` module) |
| Frontend   | HTML + CSS only — no JavaScript            |

---

## Project structure

```
Climate Action Tracker/
├── app.py                  # Routes and app logic
├── models.py                # Database access + schema + business rules
├── requirements.txt
├── database.db               # Created automatically on first run
├── static/
│   └── style.css
├── LICENCE
├── README.md
├──.gitignore                # Can be deleted no need
├── Presentation/            #If you are not a student u can be delete or you can look at it
|   ├── Presentation.pptx
|   ├── Raw Images/
|   |   ├── [images of each slide like (slide.11.jpg)]
└── templates/
    ├── base.html             # Nav, flash messages, footer
    ├── index.html            # Public landing page
    ├── register.html
    ├── login.html
    ├── dashboard.html
    ├── add_activity.html
    ├── edit_activity.html
    ├── confirm_delete.html   # No-JS delete confirmation
    └── statistics.html
```

---

## Setup

1. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   python app.py
   ```
   The database (`database.db`) and its tables are created automatically
   the first time the app runs.

4. Open **http://127.0.0.1:5000** in your browser.

Optional: set a custom session secret key before running in anything
beyond local development:
```bash
export SECRET_KEY="your-own-random-secret"   # Windows: set SECRET_KEY=...
```

---

## Routes

| Method(s)   | Route                          | Description                          |
|-------------|---------------------------------|---------------------------------------|
| GET         | `/`                              | Landing page                          |
| GET, POST   | `/register`                      | Create an account                     |
| GET, POST   | `/login`                         | Log in                                |
| GET         | `/logout`                        | Log out                               |
| GET         | `/dashboard`                     | View your activity log + score        |
| GET, POST   | `/activity/add`                  | Log a new activity                    |
| GET, POST   | `/activity/edit/<id>`            | Edit an existing activity             |
| GET         | `/activity/delete/<id>`          | Confirmation page before deleting     |
| POST        | `/activity/delete/<id>`          | Actually delete the activity          |
| GET         | `/statistics`                    | View totals, breakdown, progress bars |

---

## Activity point values

| Activity                     | Points |
|-------------------------------|--------|
| ♻️ Recycled waste              | 5      |
| 🚌 Used public transportation  | 4      |
| 🚴 Rode a bicycle              | 4      |
| 🌱 Planted a tree              | 10     |
| 💡 Saved electricity           | 3      |
| 💧 Saved water                 | 3      |

Defined once in `models.py` (`ACTIVITY_POINTS`) so scoring logic and
forms can never fall out of sync.

---

## Merge notes

This project combines three separately generated drafts:

- **Architecture** (dataclasses, schema, query helpers, `login_required`
  decorator) — taken from the cleanest of the three drafts as the base.
- **Email field on registration + statistics page layout** (stat cards,
  breakdown table, progress bars) — merged in from a second draft.
- **Friendly, personalized flash messages and nav styling** — merged in
  from a third draft.
- **Delete confirmation** was rebuilt from scratch: all three original
  drafts used a JavaScript `confirm()` popup, which was replaced with a
  plain server-rendered confirmation page to keep the whole app free of
  JavaScript.

---

## Notes on security

- Passwords are hashed with Werkzeug before being stored — plain-text
  passwords are never written to the database.
- Every activity route checks that the activity actually belongs to the
  logged-in user before allowing edits or deletes.
- Delete uses a POST request (not a GET link), which is the correct way
  to perform a state-changing action in HTTP.
