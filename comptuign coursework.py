from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import init_db, get_db
import json

app = Flask(__name__)
app.secret_key = 'stride-secret-key-2026'

# Initialize database on startup
with app.app_context():
    init_db()


@app.route('/')
def index():
    """Home page - shows today's tasks"""
    db = get_db()
    tasks = db.execute('''
        SELECT * FROM tasks 
        WHERE date(due_date) = date('now') 
        ORDER BY 
            CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
            due_date
    ''').fetchall()
    return render_template('index.html', tasks=tasks, active_page='home')

@app.route('/tasks')
def tasks():
    """Tasks page - table of all tasks with add/edit functionality"""
    db = get_db()
    all_tasks = db.execute('''
        SELECT * FROM tasks 
        ORDER BY 
            CASE status WHEN 'Not Started' THEN 1 WHEN 'In Progress' THEN 2 ELSE 3 END,
            CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
            due_date
    ''').fetchall()
    return render_template('tasks.html', tasks=all_tasks, active_page='tasks')

@app.route('/schedule')
def schedule():
    """Schedule page - auto-generated schedule based on tasks"""
    db = get_db()
    # Get settings
    settings = db.execute('SELECT * FROM settings WHERE id = 1').fetchone()
    
    # Get incomplete tasks sorted by due date and priority
    tasks = db.execute('''
        SELECT * FROM tasks 
        WHERE status != 'Completed'
        ORDER BY 
            due_date,
            CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END
    ''').fetchall()
    
    return render_template('schedule.html', tasks=tasks, settings=settings, active_page='schedule')

@app.route('/settings')
def settings():
    """Settings page - configure study time"""
    db = get_db()
    settings = db.execute('SELECT * FROM settings WHERE id = 1').fetchone()
    return render_template('settings.html', settings=settings, active_page='settings')

@app.route('/onboarding')
def onboarding():
    """Onboarding slideshow"""
    return render_template('onboarding.html')

# ============ API ROUTES ============

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.json
    db = get_db()
    db.execute('''
        INSERT INTO tasks (title, subject, status, due_date, priority, time_needed)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        data.get('title'),
        data.get('subject'),
        data.get('status', 'Not Started'),
        data.get('due_date'),
        data.get('priority', 'Medium'),
        data.get('time_needed', 1)
    ])
    db.commit()
    return jsonify({'success': True})

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    data = request.json
    db = get_db()
    db.execute('''
        UPDATE tasks 
        SET title = ?, subject = ?, status = ?, due_date = ?, priority = ?, time_needed = ?
        WHERE id = ?
    ''', [
        data.get('title'),
        data.get('subject'),
        data.get('status'),
        data.get('due_date'),
        data.get('priority'),
        data.get('time_needed'),
        task_id
    ])
    db.commit()
    return jsonify({'success': True})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', [task_id])
    db.commit()
    return jsonify({'success': True})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    data = request.json
    db = get_db()
    db.execute('''
        UPDATE settings 
        SET study_start_time = ?, study_end_time = ?, excluded_days = ?
        WHERE id = 1
    ''', [
        data.get('study_start_time'),
        data.get('study_end_time'),
        data.get('excluded_days', '')
    ])
    db.commit()
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(debug=True, port=5001)


