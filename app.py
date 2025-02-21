from flask import Flask, request, redirect, url_for, render_template, flash, session, jsonify
from Models.models import *
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Initialize DB
create_tables()

@app.route('/')  # Default route
def home():
    return redirect(url_for('login'))  # Redirect to the login page

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['register-email']
        password = request.form['register-password']
        name = request.form['name']
        qualification = request.form['qualification']
        dob = request.form['dob']

        # Check if the user already exists
        existing_user = get_user_by_username(email)
        if existing_user:
            flash('User already exists. Please log in.')
            return redirect(url_for('login'))  # Redirect to login if user exists

        # Insert new user into the database
        insert_user(email, password, name, qualification, dob)
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))  # Redirect to login after successful registration

    return render_template('login.html')  # Render registration form if GET request

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login-email']
        password = request.form['login-password']
        
        # Check for admin credentials
        if email == 'admin@gmail.com' and password == 'admin':
            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard

        user = get_user_by_username(email)
        if user and user['password'] == password:
            # Successful login logic here
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')  # This renders the login.html template

@app.route('/logout')
def logout():
    #session.clear()  # Clear the session to log out the user
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    subjects = get_subjects_with_chapters()
    return render_template('admin_dashboard.html', subjects=subjects)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')  # Placeholder for the user dashboard route

@app.route('/add_chapter', methods=['POST'])
def add_chapter():
    try:
        subject_id = request.form['subject_id']
        name = request.form['name']  # Simplified to just 'name'
        description = request.form.get('description', '')  # Made description optional
        
        add_chapter_in_db(subject_id, name, description)
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"Error: {e}")  # For debugging
        return redirect(url_for('admin_dashboard'))

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    delete_chapter_in_db(chapter_id)
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_chapter/<int:chapter_id>', methods=['POST'])
def edit_chapter(chapter_id):
    chapter_name = request.form['chapter_name']
    description = request.form.get('description', '')
    
    edit_chapter_in_db(chapter_id, chapter_name, description)
    return redirect(url_for('admin_dashboard'))

@app.route('/add_subject', methods=['POST'])
def add_subject():
    try:
        name = request.form['name']
        description = request.form.get('description', '')
        
        add_subject_in_db(name, description)
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)