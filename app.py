from flask import Flask, request, redirect, url_for, render_template, flash, session
from Models.models import create_tables, insert_user, get_user_by_username

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

    return render_template('Login.html')  # Render registration form if GET request

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

    return render_template('Login.html')  # This renders the login.html template

@app.route('/logout')
def logout():
    session.clear()  # Clear the session to log out the user
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')  # Render admin dashboard

@app.route('/dashboard')
def dashboard():
    return "Welcome to the dashboard!"  # Placeholder for the user dashboard route

if __name__ == "__main__":
    app.run(debug=True)
