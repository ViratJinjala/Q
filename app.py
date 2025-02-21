from flask import Flask, request, redirect, url_for, render_template, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from Models.models import *
from datetime import datetime

app = Flask(__name__)

# Required for flashing messages and using flask 
app.secret_key = 'your_secret_key'  

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, name, is_admin=False):
        self.id = id
        self.email = email
        self.name = name
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return User('admin', 'admin@gmail.com', 'Admin', True)
    
    user_data = get_user_by_id(user_id)
    if user_data:
        return User(
            id=user_data['id'],
            email=user_data['email'],
            name=user_data['name']
        )
    return None

## FOR SECURITY WHEN SCALING THE APPLICATION
# @app.before_request
# def check_auth():
#     if not current_user.is_authenticated and \
#        request.endpoint not in PUBLIC_ROUTES:
#         return redirect(url_for('login'))



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
            admin_user = User('admin', email, 'Admin', True)
            login_user(admin_user)
            return redirect(url_for('admin_dashboard'))

        user = get_user_by_email(email)
        if user and user['password'] == password:
            user_obj = User(
                id=user['id'],
                email=user['email'],
                name=user['name']
            )
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials. Please try again.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
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
        flash('Question added successfully!', 'success')
        return redirect(url_for('add_questions', quiz_id=quiz_id))
    except Exception as e:
        flash(f'Error adding question: {str(e)}', 'error')
        return redirect(url_for('add_questions', quiz_id=quiz_id))

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
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    quizzes = get_available_quizzes()
    return render_template('dashboard.html', quizzes=quizzes)

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
        return render_template('add_quiz.html', 
                            chapters=chapters,
                            selected_subject=subject_id)
    except Exception as e:
        flash(f'Error loading chapters: {str(e)}', 'error')
        return redirect(url_for('add_quiz'))

@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    try:
        delete_question_in_db(question_id)
        flash('Question deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting question: {str(e)}', 'error')
    return redirect(url_for('admin_quiz_management'))

@app.route('/start_quiz/<int:quiz_id>')
@login_required
def start_quiz(quiz_id):
    try:
        # Get quiz details
        quiz = get_quiz_by_id(quiz_id)
        if not quiz:
            flash('Quiz not found.', 'error')
            return redirect(url_for('dashboard'))

        # Get questions
        questions = get_quiz_questions(quiz_id)
        if not questions:
            flash('No questions found for this quiz.', 'error')
            return redirect(url_for('dashboard'))

        # Store quiz data in session
        session['current_quiz'] = {
            'quiz_id': quiz_id,
            'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Redirect to first question
        return redirect(url_for('quiz', quiz_id=quiz_id, q=0))

    except Exception as e:
        flash(f'Error starting quiz: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/quiz/<int:quiz_id>')
def quiz(quiz_id):
    try:
        # Get current question number from query params
        current_q = request.args.get('q', 0, type=int)
        
        # Get quiz details
        quiz = get_quiz_by_id(quiz_id)
        if not quiz:
            flash('Quiz not found.', 'error')
            return redirect(url_for('dashboard'))

        # Get all questions
        questions = get_quiz_questions(quiz_id)
        if not questions:
            flash('No questions found for this quiz.', 'error')
            return redirect(url_for('dashboard'))

        total_questions = len(questions)
        
        # Validate question number
        if current_q >= total_questions:
            flash('Invalid question number.', 'error')
            return redirect(url_for('dashboard'))

        # Initialize quiz session if not already started
        if 'current_quiz' not in session:
            session['current_quiz'] = {
                'quiz_id': quiz_id,
                'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        return render_template('quiz.html', 
                             quiz=quiz,
                             questions=questions,
                             current_q=current_q,
                             total_questions=total_questions)

    except Exception as e:
        flash(f'Error loading quiz: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    try:
        # Get all questions for this quiz
        questions = get_quiz_questions(quiz_id)
        total_questions = len(questions)
        correct_answers = 0

        # Calculate score
        for question in questions:
            user_answer = request.form.get(f'answer_{question["id"]}')
            if user_answer and int(user_answer) == question['correct_option']:
                correct_answers += 1

        # Calculate percentage
        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Save to database
        save_quiz_score(
            quiz_id=quiz_id,
            user_id=current_user.id,
            score=score_percentage,
            correct_answers=correct_answers,
            total_questions=total_questions
        )

        # Store result in flash message
        flash({
            'type': 'quiz_result',
            'score': round(score_percentage, 1),
            'correct': correct_answers,
            'total': total_questions
        })

        return redirect(url_for('dashboard'))
        
    except Exception as e:
        flash('Error submitting quiz. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/quiz_result')
@login_required
def quiz_result():
    result = session.get('last_quiz_result')
    if not result:
        return redirect(url_for('dashboard'))
    
    # Clear the result from session after displaying
    session.pop('last_quiz_result', None)
    
    return render_template('quiz_result.html', result=result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8003, debug=True)