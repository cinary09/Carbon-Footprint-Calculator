from flask import Flask, render_template, request, redirect, url_for, session, flash
import models

app = Flask(__name__)
app.secret_key = 'climate_action_tracker_secure_secret_key_2026'

models.init_db()

ACTIVITY_POINTS = {
    "Recycled waste": 5,
    "Used public transportation": 4,
    "Rode a bicycle": 4,
    "Planted a tree": 10,
    "Saved electricity": 3,
    "Saved water": 3
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if not username or not password:
            flash('Please fill out all fields.', 'error')
            return redirect(url_for('register'))
            
        if models.create_user(username, password):
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username is already taken.', 'error')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        user = models.verify_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to view your dashboard.', 'error')
        return redirect(url_for('login'))
        
    activities = models.get_user_activities(session['user_id'])
    stats = models.get_user_stats(session['user_id'])
    return render_template('dashboard.html', activities=activities, total_score=stats['total_points'])

@app.route('/activity/add', methods=['GET', 'POST'])
def add_activity():
    if 'user_id' not in session:
        flash('Authentication required.', 'error')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        activity_type = request.form['activity_type']
        description = request.form['description'].strip()
        
        if activity_type not in ACTIVITY_POINTS:
            flash('Invalid action choice selected.', 'error')
            return redirect(url_for('add_activity'))
            
        points = ACTIVITY_POINTS[activity_type]
        models.add_activity(session['user_id'], activity_type, points, description)
        flash('Activity logged successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('add_activity.html', options=ACTIVITY_POINTS.keys())

@app.route('/activity/edit/<int:activity_id>', methods=['GET', 'POST'])
def edit_activity(activity_id):
    if 'user_id' not in session:
        flash('Authentication required.', 'error')
        return redirect(url_for('login'))
        
    activity = models.get_activity(activity_id, session['user_id'])
    if not activity:
        flash('Record not found.', 'error')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        activity_type = request.form['activity_type']
        description = request.form['description'].strip()
        
        if activity_type not in ACTIVITY_POINTS:
            flash('Invalid action choice selected.', 'error')
            return redirect(url_for('edit_activity', activity_id=activity_id))
            
        points = ACTIVITY_POINTS[activity_type]
        models.update_activity(activity_id, session['user_id'], activity_type, points, description)
        flash('Activity record updated safely.', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('edit_activity.html', activity=activity, options=ACTIVITY_POINTS.keys())

@app.route('/activity/delete/<int:activity_id>', methods=['POST'])
def delete_activity(activity_id):
    if 'user_id' not in session:
        flash('Authentication required.', 'error')
        return redirect(url_for('login'))
        
    models.delete_activity(activity_id, session['user_id'])
    flash('Activity record removed.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/statistics')
def statistics():
    if 'user_id' not in session:
        flash('Please log in to view statistics.', 'error')
        return redirect(url_for('login'))
        
    stats = models.get_user_stats(session['user_id'])
    return render_template('statistics.html', stats=stats)

if __name__ == '__main__':  
    app.run(debug=True) 
        