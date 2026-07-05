# 🌍 Climate Action Tracker

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.x-black.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A lightweight Flask web application that helps users record everyday climate-friendly actions, earn points, and monitor their environmental impact through an intuitive dashboard and detailed statistics.

Designed with simplicity, security, and accessibility in mind, the application is built using **Flask**, **Jinja2**, **Werkzeug**, and **SQLite**, with **zero JavaScript**.

---

## ✨ Features

### 👤 User Accounts
- Secure registration and login
- Password hashing using Werkzeug
- Session-based authentication

### 🌱 Climate Activity Tracking
- Add, edit, and delete activities
- Record activity dates and optional notes
- Multiple predefined climate-positive actions

### 🏆 Point System
- Automatic point calculation
- Running total displayed on the dashboard
- Consistent scoring across the application

### 📊 Statistics Dashboard
- Total points earned
- Total activities completed
- Most frequently logged activity
- Average points per activity
- Activity breakdown table
- Visual progress bars

### 💬 User Feedback
- Flash messages for successful and failed actions
- Personalized welcome message after login

### 🚫 Zero JavaScript
Every feature is implemented entirely with:

- Flask
- Jinja2
- HTML
- CSS

Even delete confirmation is handled through a dedicated server-rendered confirmation page instead of JavaScript dialogs.

---

# 🛠 Tech Stack

| Component | Technology |
|------------|------------|
| Backend | Flask |
| Templates | Jinja2 |
| Authentication | Werkzeug Security |
| Database | SQLite (`sqlite3`) |
| Frontend | HTML5 + CSS3 |
| JavaScript | None |

---

# 📁 Project Structure

```text
Climate Action Tracker/
│
├── app.py                     # Application routes
├── models.py                  # Database logic & business rules
├── requirements.txt
├── database.db                # Auto-created on first launch
│
├── static/
│   └── style.css
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── add_activity.html
│   ├── edit_activity.html
│   ├── confirm_delete.html
│   └── statistics.html
│
├── Presentation/              # Optional presentation materials
│   ├── Presentation.pptx
│   └── Raw Images/
│
├── LICENSE
├── README.md
└── .gitignore
```

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/yourusername/climate-action-tracker.git

cd climate-action-tracker
```

---

## 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run the application

```bash
python app.py
```

The SQLite database is automatically created during the first launch.

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## 🔐 Optional Environment Variable

For production or deployment, set a custom secret key:

**Linux / macOS**

```bash
export SECRET_KEY="your-random-secret"
```

**Windows**

```cmd
set SECRET_KEY=your-random-secret
```

---

# 🌿 Activity Point Values

| Activity | Points |
|----------|-------:|
| ♻️ Recycled Waste | 5 |
| 🚌 Used Public Transportation | 4 |
| 🚴 Rode a Bicycle | 4 |
| 🌱 Planted a Tree | 10 |
| 💡 Saved Electricity | 3 |
| 💧 Saved Water | 3 |

Point values are centrally defined in `models.py` to ensure consistency throughout the application.

---

# 📌 Application Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Home page |
| GET, POST | `/register` | Register a new account |
| GET, POST | `/login` | User login |
| GET | `/logout` | Logout |
| GET | `/dashboard` | Dashboard |
| GET, POST | `/activity/add` | Add activity |
| GET, POST | `/activity/edit/<id>` | Edit activity |
| GET | `/activity/delete/<id>` | Delete confirmation |
| POST | `/activity/delete/<id>` | Delete activity |
| GET | `/statistics` | Statistics page |

---

# 🔒 Security

The application follows several security best practices:

- Passwords are hashed using Werkzeug.
- Plain-text passwords are never stored.
- User sessions are securely managed.
- Users may only edit or delete their own activities.
- Destructive actions use POST requests.
- Authentication is enforced for protected routes.

---

# 🤝 Contributing

Contributions are welcome!

If you'd like to improve the project:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

---

# 📄 License

This project is licensed under the MIT License.

See the **LICENSE** file for additional information.

---

# 👨‍💻 Author

Created by **cinary09**

GitHub: https://github.com/cinary09

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub. It helps support future improvements and new projects.
