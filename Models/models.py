from Models.database import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            qualification TEXT,
            dob TEXT
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id INTEGER NOT NULL,
            date_of_quiz TEXT,
            time_duration TEXT,
            remarks TEXT,
            FOREIGN KEY (chapter_id) REFERENCES chapters (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_statement TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            correct_option INTEGER NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            time_stamp TEXT,
            total_score INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()

def insert_user(email, password, name, qualification, dob):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email, password, name, qualification, dob) VALUES (?, ?, ?, ?, ?)",
                   (email, password, name, qualification, dob))
    conn.commit()
    conn.close()

def get_user_by_username(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()  # Fetch one user
    conn.close()
    return user

# all this for admin dashboard
def get_subjects_with_chapters():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Modified query to correctly count questions
    query = """
    SELECT 
        s.id as subject_id,
        s.name as subject_name,
        c.id as chapter_id,
        c.name as chapter_name,
        (
            SELECT COUNT(*)
            FROM questions q2
            JOIN quizzes qz ON q2.quiz_id = qz.id
            WHERE qz.chapter_id = c.id
        ) as question_count
    FROM subjects s
    LEFT JOIN chapters c ON s.id = c.subject_id
    ORDER BY s.id, c.id
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Organize the data into a nested structure
    subjects = {}
    for row in rows:
        if row['subject_id'] not in subjects:
            subjects[row['subject_id']] = {
                'id': row['subject_id'],
                'name': row['subject_name'],
                'chapters': []
            }
        
        if row['chapter_id']:  # Only add chapter if it exists
            subjects[row['subject_id']]['chapters'].append({
                'id': row['chapter_id'],
                'name': row['chapter_name'],
                'questions': row['question_count'] or 0
            })
    
    conn.close()
    return list(subjects.values())

def add_chapter_in_db(subject_id, name, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chapters (subject_id, name, description)
        VALUES (?, ?, ?)
    """, (subject_id, name, description))
    conn.commit()
    conn.close()

def delete_chapter_in_db(chapter_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))
    conn.commit()
    conn.close()

def edit_chapter_in_db(chapter_id, name, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chapters 
        SET name = ?, description = ?
        WHERE id = ?
    """, (name, description, chapter_id))
    conn.commit()
    conn.close()

def get_chapter_by_id(chapter_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM chapters WHERE id = ?
    """, (chapter_id,))
    chapter = cursor.fetchone()
    conn.close()
    return chapter

def add_subject_in_db(name, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO subjects (name, description)
        VALUES (?, ?)
    """, (name, description))
    conn.commit()
    conn.close()