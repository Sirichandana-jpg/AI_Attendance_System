import sqlite3
import os
import json

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "attendance_system.db")

def get_connection():
    return sqlite3.connect(DB_FILE)

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Table: students
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table: face_embeddings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            embedding TEXT NOT NULL,
            model_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')

    # Table: attendance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            source TEXT,
            confidence REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

# ---------------- Student Operations ----------------

def add_student(student_id, name, department):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (student_id, name, department) VALUES (?, ?, ?)",
            (student_id, name, department)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_students():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return [dict(s) for s in students]

def get_student_by_id(student_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    return dict(student) if student else None

# ---------------- Embedding Operations ----------------

def add_embedding(student_id, embedding, model_name):
    # Store embedding as JSON string
    embedding_json = json.dumps(embedding)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO face_embeddings (student_id, embedding, model_name) VALUES (?, ?, ?)",
        (student_id, embedding_json, model_name)
    )
    conn.commit()
    conn.close()

def get_all_embeddings():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM face_embeddings")
    rows = cursor.fetchall()
    conn.close()
    
    embeddings_list = []
    for row in rows:
        data = dict(row)
        data['embedding'] = json.loads(data['embedding'])
        embeddings_list.append(data)
    return embeddings_list

# ---------------- Attendance Operations ----------------

def add_attendance(student_id, date, time, source, confidence, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO attendance (student_id, date, time, source, confidence, status) VALUES (?, ?, ?, ?, ?, ?)",
        (student_id, date, time, source, confidence, status)
    )
    conn.commit()
    conn.close()

def get_attendance_by_date(date):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.id, a.student_id, s.name, s.department, a.date, a.time, a.source, a.confidence, a.status 
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.date = ?
    ''', (date,))
    records = cursor.fetchall()
    conn.close()
    return [dict(r) for r in records]

def has_attended_today(student_id, date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ? AND date = ?", (student_id, date))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# Initialize immediately on import
if __name__ != "__main__":
    initialize_database()
