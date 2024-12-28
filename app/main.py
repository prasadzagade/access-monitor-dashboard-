from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import log_parser
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

from collections import defaultdict

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        logs = log_parser.parse_logs()
        search_ip = request.args.get('search_ip')

        if search_ip:
            logs = [log for log in logs if log['ip'] == search_ip]

        # Group logs by date with the format DD-MM-YYYY
        grouped_logs = defaultdict(list)
        for log in logs:
            date_key = log['date'].strftime('%d-%m-%Y')  # Format as DD-MM-YYYY
            grouped_logs[date_key].append(log)

        return render_template('dashboard.html', grouped_logs=grouped_logs)
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/get_logs')
@login_required
def get_logs():
    logs = log_parser.parse_logs()
    search_ip = request.args.get('search_ip')
    if search_ip:
        logs = [log for log in logs if log['ip'] == search_ip]
    return jsonify([{**log, 'date': log['date'].isoformat()} for log in logs])

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
