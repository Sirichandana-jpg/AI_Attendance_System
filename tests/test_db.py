import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import database

def test_db():
    print("Initializing Database...")
    database.initialize_database()
    
    print("Adding student...")
    success = database.add_student("202601", "Rahul Kumar", "CSE")
    print(f"Add student success: {success}")
    
    print("Adding duplicate student (should fail)...")
    success2 = database.add_student("202601", "Rahul Kumar", "CSE")
    print(f"Add duplicate student success: {success2}")
    
    print("Fetching student...")
    student = database.get_student_by_id("202601")
    print(f"Student: {student}")
    
    print("Adding embedding...")
    database.add_embedding("202601", [0.1, 0.2, 0.3], "VGG-Face")
    embeddings = database.get_all_embeddings()
    print(f"Embeddings: {embeddings}")
    
    print("Adding attendance...")
    database.add_attendance("202601", "2026-08-27", "09:00:00", "camera_1", 0.95, "Present")
    
    print("Fetching attendance...")
    att = database.get_attendance_by_date("2026-08-27")
    print(f"Attendance: {att}")
    
    print("Test Complete.")

if __name__ == "__main__":
    test_db()
