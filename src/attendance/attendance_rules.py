from src.database import database
from src.utils.config_manager import get_config_value
import time

# Dictionary to hold the last marked time for a student to implement cooldown
# Format: { "student_id": timestamp }
_recent_attendance_cache = {}

def can_mark_attendance(student_id, date, current_timestamp=None):
    """
    Check if attendance can be marked based on duplication prevention rules.
    """
    duplicate_prevention = get_config_value("attendance", "duplicate_prevention", True)
    cooldown_seconds = get_config_value("attendance", "cooldown_seconds", 60)
    
    if current_timestamp is None:
        current_timestamp = time.time()
        
    if duplicate_prevention:
        # Check database if they already attended today
        if database.has_attended_today(student_id, date):
            return False
            
    # Check cooldown cache (useful if duplicate prevention is off but we still don't want spam)
    last_marked = _recent_attendance_cache.get(student_id, 0)
    if current_timestamp - last_marked < cooldown_seconds:
        return False
        
    return True
    
def update_attendance_cache(student_id, current_timestamp=None):
    if current_timestamp is None:
        current_timestamp = time.time()
    _recent_attendance_cache[student_id] = current_timestamp
