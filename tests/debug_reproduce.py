import cv2
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.video.video_processor import VideoProcessor
from src.database import database

def on_event(msg):
    print(f"EVENT: {msg}")

def run_debug(video_path):
    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        return

    print(f"Starting video processor for {video_path}...")
    vp = VideoProcessor(source=video_path, on_event_callback=on_event)
    
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        if vp.resize_width:
            h, w = frame.shape[:2]
            if w > vp.resize_width:
                scale = vp.resize_width / w
                frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
                
        tracked_persons = vp.tracker.track(frame)
        
        for person in tracked_persons:
            track_id = person['track_id']
            x1, y1, x2, y2 = person['bbox']
            
            margin_y = int((y2 - y1) * 0.1)
            margin_x = int((x2 - x1) * 0.1)
            y1_padded = max(0, y1 - margin_y)
            y2_padded = min(frame.shape[0], y2 + margin_y)
            x1_padded = max(0, x1 - margin_x)
            x2_padded = min(frame.shape[1], x2 + margin_x)
            
            person_crop = frame[y1_padded:y2_padded, x1_padded:x2_padded].copy()
            
            if person_crop.size > 0:
                # To see raw distances, let's inject a print inside or just call recognize
                student_id, name, conf = vp.recognizer.recognize(person_crop)
                print(f"Frame: {frame_count} | Track: {track_id} | Crop size: {person_crop.shape} | ID: {student_id} | Name: {name} | Conf: {conf}")

        if frame_count > 30:
            break

    cap.release()

if __name__ == "__main__":
    database.initialize_database()
    if len(sys.argv) > 1:
        run_debug(sys.argv[1])
    else:
        print("Provide video path")
