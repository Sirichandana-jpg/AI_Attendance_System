import datetime
import time
from src.database import database
from src.attendance.attendance_rules import can_mark_attendance, update_attendance_cache

class AttendanceManager:
    def __init__(self, source_name="CCTV"):
        self.source_name = source_name
        
    def process_recognition(self, student_id, student_name, confidence):
        """
        Process a recognized student and mark attendance if rules allow.
        """
        if student_id == "Unknown" or student_name == "Unknown":
            return False
            
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        timestamp = time.time()
        
        if can_mark_attendance(student_id, date_str, timestamp):
            # Mark attendance
            database.add_attendance(
                student_id=student_id,
                date=date_str,
                time=time_str,
                source=self.source_name,
                confidence=confidence,
                status="Present"
            )
            update_attendance_cache(student_id, timestamp)
            print(f"Attendance marked for {student_name} ({student_id}) at {time_str}")
            return True
            
        return False
        
    def get_todays_report(self):
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        return database.get_attendance_by_date(date_str)
        
    def get_absent_students(self):
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        all_students = database.get_all_students()
        present_records = database.get_attendance_by_date(date_str)
        
        present_ids = {record['student_id'] for record in present_records}
        
        absent_students = []
        for student in all_students:
            if student['student_id'] not in present_ids:
                absent_students.append(student)
                
        return absent_students
