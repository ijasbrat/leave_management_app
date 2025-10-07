from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',          # your MySQL user
        password='root',      # your MySQL password
        database='user_auth'  # your database name
    )
    return conn

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Manager Login (Sign In)
@app.route('/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']

    if email == 'admin@gmail.com' and password == 'admin':
        session['loggedin'] = True
        session['email'] = email
        session['role'] = 'manager'
        flash('Manager login successful!', 'success')
        return redirect(url_for('dashboard_manager'))
    else:
        flash('Incorrect Manager credentials!', 'error')
        return redirect(url_for('index'))

# User Login (Log In)
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    if email == 'user1@gmail.com.com' and password == 'user1':
        session['loggedin'] = True
        session['email'] = email
        session['role'] = 'user'
        flash('User login successful!', 'success')
        return redirect(url_for('dashboard_user'))
    else:
        flash('Incorrect User credentials!', 'error')
        return redirect(url_for('index'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

# Manager Dashboard
@app.route('/dashboard_manager')
def dashboard_manager():
    if 'loggedin' in session and session['role'] == 'manager':
        return render_template('dashboard_manager.html')
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

# User Dashboard
@app.route('/dashboard_user')
def dashboard_user():
    if 'loggedin' in session and session['role'] == 'user':
        return render_template('dashboard_user.html')
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

# User - Apply Leave
@app.route('/leave_form', methods=['GET', 'POST'])
def leave_form():
    if 'loggedin' in session and session['role'] == 'user':
        if request.method == 'POST':
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            reason = request.form['reason']

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO leave_requests (user_email, start_date, end_date, reason) VALUES (%s, %s, %s, %s)",
                        (session['email'], start_date, end_date, reason))
            conn.commit()
            cur.close()
            conn.close()

            flash('Leave application submitted successfully!', 'success')
            return redirect(url_for('leave_management_user'))

        return render_template('leave_form.html')
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

# User - View Own Leaves
@app.route('/leave_management_user')
def leave_management_user():
    if 'loggedin' in session and session['role'] == 'user':
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM leave_requests WHERE user_email = %s", (session['email'],))
        leaves = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('leave_management_user.html', leaves=leaves)
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

# Manager - View All Leaves
@app.route('/leave_management_manager')
def leave_management_manager():
    if 'loggedin' in session and session['role'] == 'manager':
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM leave_requests")
        leaves = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('leave_management_manager.html', leaves=leaves)
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

# Manager - Accept Leave
@app.route('/accept_leave/<int:id>')
def accept_leave(id):
    if 'loggedin' in session and session['role'] == 'manager':
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE leave_requests SET status = 'Accepted' WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Leave accepted.', 'success')
        return redirect(url_for('leave_management_manager'))
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

# Manager - Reject Leave
@app.route('/reject_leave/<int:id>')
def reject_leave(id):
    if 'loggedin' in session and session['role'] == 'manager':
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE leave_requests SET status = 'Rejected' WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Leave rejected.', 'success')
        return redirect(url_for('leave_management_manager'))
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

# Manager - View Employee List
@app.route('/employee_list')
def employee_list():
    if 'loggedin' in session and session['role'] == 'manager':
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT DISTINCT user_email FROM leave_requests")
        employees = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('employee_list.html', employees=employees)
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

# Manager - View Individual Employee Leaves
@app.route('/employee/<string:email>')
def employee_profile(email):
    if 'loggedin' in session and session['role'] == 'manager':
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM leave_requests WHERE user_email = %s", (email,))
        leaves = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('employee_profile.html', leaves=leaves, employee_email=email)
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
