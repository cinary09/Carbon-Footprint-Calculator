from datetime import date
from functools import wraps
import os

from flask import Flask, flash, g, redirect, render_template, request, session, url_for

from models import (
    create_activity,
    create_user,
    delete_activity,
    get_activity_by_id,
    get_db_path,
    get_user_activities,
    get_user_by_id,
    get_user_by_username,
    get_user_statistics,
    init_db,
    update_activity,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "climate-action-tracker-secret-key")
app.config["DATABASE"] = get_db_path()

ACTIVITY_POINTS = {
    "Recycled waste": 5,
    "Used public transportation": 4,
    "Rode a bicycle": 4,
    "Planted a tree": 10,
    "Saved electricity": 3,
    "Saved water": 3,
}


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = get_user_by_id(user_id) if user_id else None


def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password or not confirm_password:
            flash("All fields are required.", "error")
        elif len(username) < 3:
            flash("Username must be at least 3 characters long.", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        elif get_user_by_username(username) is not None:
            flash("That username is already taken.", "error")
        else:
            create_user(username, password)
            flash("Account created successfully. You can log in now.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)
        if user is None or not user.check_password(password):
            flash("Invalid username or password.", "error")
        else:
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    activities = get_user_activities(g.user.id)
    total_points = sum(activity.points for activity in activities)
    return render_template(
        "dashboard.html",
        activities=activities,
        total_points=total_points,
        activity_points=ACTIVITY_POINTS,
    )


@app.route("/activity/add", methods=["GET", "POST"])
@login_required
def add_activity():
    if request.method == "POST":
        activity_type = request.form.get("activity_type", "")
        activity_date = request.form.get("activity_date", str(date.today()))
        notes = request.form.get("notes", "").strip()

        if activity_type not in ACTIVITY_POINTS:
            flash("Please select a valid activity.", "error")
        else:
            points = ACTIVITY_POINTS[activity_type]
            create_activity(g.user.id, activity_type, points, activity_date, notes)
            flash("Activity added successfully.", "success")
            return redirect(url_for("dashboard"))

    return render_template("add_activity.html", activity_points=ACTIVITY_POINTS, today=str(date.today()))


@app.route("/activity/edit/<int:activity_id>", methods=["GET", "POST"])
@login_required
def edit_activity(activity_id):
    activity = get_activity_by_id(activity_id)

    if activity is None or activity.user_id != g.user.id:
        flash("Activity not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        activity_type = request.form.get("activity_type", "")
        activity_date = request.form.get("activity_date", activity.activity_date)
        notes = request.form.get("notes", "").strip()

        if activity_type not in ACTIVITY_POINTS:
            flash("Please select a valid activity.", "error")
        else:
            points = ACTIVITY_POINTS[activity_type]
            update_activity(activity_id, activity_type, points, activity_date, notes)
            flash("Activity updated successfully.", "success")
            return redirect(url_for("dashboard"))

    return render_template("edit_activity.html", activity=activity, activity_points=ACTIVITY_POINTS)


@app.route("/activity/delete/<int:activity_id>", methods=["POST"])
@login_required
def delete_activity_route(activity_id):
    activity = get_activity_by_id(activity_id)

    if activity is None or activity.user_id != g.user.id:
        flash("Activity not found.", "error")
    else:
        delete_activity(activity_id)
        flash("Activity deleted successfully.", "success")

    return redirect(url_for("dashboard"))


@app.route("/statistics")
@login_required
def statistics():
    stats = get_user_statistics(g.user.id)
    activities = get_user_activities(g.user.id)
    total_points = stats["total_points"]
    total_activities = stats["total_activities"]
    most_common_activity = stats["most_common_activity"]

    if total_activities == 0:
        progress_summary = "Start by adding your first climate-positive action."
    elif total_points >= 50:
        progress_summary = "Excellent progress. Your actions are building a strong positive impact."
    elif total_points >= 20:
        progress_summary = "You are making solid progress with consistent sustainable choices."
    else:
        progress_summary = "Great start. Keep logging activities to grow your impact."

    return render_template(
        "statistics.html",
        total_activities=total_activities,
        total_points=total_points,
        most_common_activity=most_common_activity,
        progress_summary=progress_summary,
        activities=activities,
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
