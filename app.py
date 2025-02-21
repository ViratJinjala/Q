from flask import Flask, request, redirect, url_for, render_template, flash, session, jsonify
from Models.models import *
from datetime import datetime
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


# main page for quiz management
@app.route('/admin_quiz_management')
def admin_quiz_management():
    subjects = get_all_subjects()
    quizzes = get_quizzes()
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin_quiz_management.html', 
                         subjects=subjects, 
                         quizzes=quizzes, 
                         today_date=today_date)

@app.route('/search_quiz')
def search_quiz():
    query = request.args.get('q')
    quizzes = search_quizzes(query)
    return render_template('admin_quiz_management.html', quizzes=quizzes)

@app.route('/add_question/<int:quiz_id>', methods=['POST'])
def add_question(quiz_id):
    try:
        question_data = {
            'quiz_id': quiz_id,
            'question_statement': request.form['question_statement'],
            'option1': request.form['option1'],
            'option2': request.form['option2'],
            'option3': request.form['option3'],
            'option4': request.form['option4'],
            'correct_option': int(request.form['correct_option'])
        }
        
        add_question_in_db(**question_data)
        return jsonify({'success': True, 'message': 'Question added successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error adding question: {str(e)}'})

@app.route('/add_quiz', methods=['POST'])
def add_quiz():
    try:
        quiz_data = {
            'chapter_id': request.form['chapter_id'],
            'quiz_date': request.form['quiz_date'],
            'quiz_duration': int(request.form['quiz_duration']),
            'passing_score': int(request.form['passing_score']),
            'max_attempts': int(request.form['max_attempts']),
            'instructions': request.form.get('instructions', ''),
            'status': request.form['status']
        }
        
        add_quiz_in_db(**quiz_data)
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('admin_quiz_management'))
    except Exception as e:
        flash(f'Error adding quiz: {str(e)}', 'error')
        return redirect(url_for('admin_quiz_management'))

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

@app.route('/scores')
def scores():
    return render_template('scores.html')

@app.route('/get_chapters/<int:subject_id>')
def get_chapters(subject_id):
    try:
        chapters = get_chapters_by_subject(subject_id)
        return jsonify([{
            'id': chapter['id'],
            'name': chapter['name'],
            'subject_name': chapter['subject_name']
        } for chapter in chapters])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    try:
        delete_question_in_db(question_id)
        flash('Question deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting question: {str(e)}', 'error')
    return redirect(url_for('admin_quiz_management'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8002, debug=True)