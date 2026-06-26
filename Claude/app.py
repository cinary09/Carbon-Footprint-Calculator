from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import models
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'climate_action_tracker_secret_key'

models.init_db()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters long.'
        
        if error is None:
            existing_user = models.get_user_by_username(username)
            if existing_user:
                error = 'Username already exists.'
            else:
                password_hash = generate_password_hash(password)
                models.create_user(username, email, password_hash)
                return redirect(url_for('login'))
        
        return render_template('register.html', error=error, username=username, email=email)
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            user = models.get_user_by_username(username)
            
            if user and check_password_hash(user['password'], password):
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid username or password.'
        
        return render_template('login.html', error=error, username=username)
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    activities = models.get_user_activities(user_id)
    total_points = models.get_user_total_points(user_id)
    
    activities_with_names = []
    for activity in activities:
        activity_dict = dict(activity)
        activity_dict['activity_name'] = models.get_activity_display_name(activity['activity_type'])
        activities_with_names.append(activity_dict)
    
    return render_template('dashboard.html', activities=activities_with_names, total_points=total_points)


@app.route('/add-activity', methods=['GET', 'POST'])
@login_required
def add_activity():
    if request.method == 'POST':
        activity_type = request.form.get('activity_type', '').strip()
        description = request.form.get('description', '').strip()
        
        error = None
        
        if not activity_type:
            error = 'Activity type is required.'
        elif activity_type not in models.ACTIVITY_POINTS:
            error = 'Invalid activity type.'
        
        if error is None:
            user_id = session['user_id']
            models.add_activity(user_id, activity_type, description)
            return redirect(url_for('dashboard'))
        
        return render_template('add_activity.html', error=error, activity_types=models.ACTIVITY_NAMES, activity_type=activity_type, description=description)
    
    return render_template('add_activity.html', activity_types=models.ACTIVITY_NAMES)


@app.route('/edit-activity/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def edit_activity(activity_id):
    activity = models.get_activity_by_id(activity_id)
    
    if not activity:
        return redirect(url_for('dashboard'))
    
    if activity['user_id'] != session['user_id']:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        activity_type = request.form.get('activity_type', '').strip()
        description = request.form.get('description', '').strip()
        
        error = None
        
        if not activity_type:
            error = 'Activity type is required.'
        elif activity_type not in models.ACTIVITY_POINTS:
            error = 'Invalid activity type.'
        
        if error is None:
            models.update_activity(activity_id, activity_type, description)
            return redirect(url_for('dashboard'))
        
        return render_template('edit_activity.html', activity=activity, error=error, activity_types=models.ACTIVITY_NAMES, activity_type=activity_type, description=description)
    
    return render_template('edit_activity.html', activity=activity, activity_types=models.ACTIVITY_NAMES)


@app.route('/delete-activity/<int:activity_id>')
@login_required
def delete_activity(activity_id):
    activity = models.get_activity_by_id(activity_id)
    
    if activity and activity['user_id'] == session['user_id']:
        models.delete_activity(activity_id)
    
    return redirect(url_for('dashboard'))


@app.route('/statistics')
@login_required
def statistics():
    user_id = session['user_id']
    total_activities = models.get_user_activity_count(user_id)
    total_points = models.get_user_total_points(user_id)
    most_common = models.get_user_most_common_activity(user_id)
    
    activities = models.get_user_activities(user_id)
    activity_breakdown = {}
    
    for activity in activities:
        activity_name = models.get_activity_display_name(activity['activity_type'])
        if activity_name not in activity_breakdown:
            activity_breakdown[activity_name] = {'count': 0, 'points': 0}
        activity_breakdown[activity_name]['count'] += 1
        activity_breakdown[activity_name]['points'] += activity['points']
    
    return render_template('statistics.html', total_activities=total_activities, total_points=total_points, most_common=most_common, activity_breakdown=activity_breakdown)


if __name__ == '__main__':
    app.run(debug=True)