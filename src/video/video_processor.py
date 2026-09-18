import cv2
import threading
import time
from src.tracking.tracker import PersonTracker
from src.recognition.face_recognition import FaceRecognizer
from src.attendance.attendance_manager import AttendanceManager
from src.utils.config_manager import get_config_value

class VideoProcessor:
    def __init__(self, source=0, on_frame_callback=None, on_event_callback=None):
        self.source = source
        self.on_frame_callback = on_frame_callback
        self.on_event_callback = on_event_callback
        
        self.tracker = PersonTracker()
        self.recognizer = FaceRecognizer()
        self.attendance_manager = AttendanceManager(source_name=str(source))
        
        self.frame_skip = get_config_value("video", "frame_skip", 2)
        self.resize_width = get_config_value("video", "resize_width", 640)
        
        self.is_running = False
        self.is_paused = False
        self._thread = None
        
        self.track_identities = {} # track_id -> {"name": "...", "confidence": 0.0, "student_id": "..."}

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            # Reload embeddings in case new students were registered
            self.recognizer.reload_embeddings()
            self._thread = threading.Thread(target=self._process_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def _process_loop(self):
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            if self.on_event_callback:
                self.on_event_callback("Error: Cannot open video source.")
            self.is_running = False
            return
            
        frame_count = 0
        fps_start_time = time.time()
        fps_frames = 0
        current_fps = 0
        
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue
                
            ret, frame = cap.read()
            if not ret:
                break
                
            # Resize for performance
            if self.resize_width:
                h, w = frame.shape[:2]
                if w > self.resize_width:
                    scale = self.resize_width / w
                    frame = cv2.resize(frame, (int(w * scale), int(h * scale)))

            frame_count += 1
            fps_frames += 1
            
            # Calculate FPS
            if time.time() - fps_start_time >= 1.0:
                current_fps = fps_frames
                fps_frames = 0
                fps_start_time = time.time()
                
            # Only process tracking on specific frames, or all frames but skip heavy recognition
            tracked_persons = self.tracker.track(frame)
            
            # Periodically try to recognize unknown tracks
            if frame_count % (self.frame_skip + 1) == 0:
                for person in tracked_persons:
                    track_id = person['track_id']
                    x1, y1, x2, y2 = person['bbox']
                    
                    # If not recognized yet or confidence is low, attempt recognition
                    current_id_info = self.track_identities.get(track_id, None)
                    if not current_id_info or current_id_info['student_id'] == "Unknown":
                        
                        # Pass a padded person crop so DeepFace can detect and align the face properly
                        margin_y = int((y2 - y1) * 0.1)
                        margin_x = int((x2 - x1) * 0.1)
                        y1_padded = max(0, y1 - margin_y)
                        y2_padded = min(frame.shape[0], y2 + margin_y)
                        x1_padded = max(0, x1 - margin_x)
                        x2_padded = min(frame.shape[1], x2 + margin_x)
                        
                        person_crop = frame[y1_padded:y2_padded, x1_padded:x2_padded].copy()
                        
                        if person_crop.size > 0:
                            student_id, name, conf = self.recognizer.recognize(person_crop)
                            
                            if student_id != "Unknown":
                                self.track_identities[track_id] = {
                                    "student_id": student_id,
                                    "name": name,
                                    "confidence": conf
                                }
                                # Mark attendance
                                success = self.attendance_manager.process_recognition(student_id, name, conf)
                                if success and self.on_event_callback:
                                    self.on_event_callback(f"Marked: {name} (Track: {track_id})")
                            else:
                                self.track_identities[track_id] = {
                                    "student_id": "Unknown",
                                    "name": "Unknown",
                                    "confidence": conf
                                }
            
            # Draw boxes and IDs
            for person in tracked_persons:
                track_id = person['track_id']
                x1, y1, x2, y2 = person['bbox']
                
                info = self.track_identities.get(track_id, {"name": "Unknown", "confidence": 0.0})
                
                color = (0, 255, 0) if info['name'] != "Unknown" else (0, 0, 255)
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"Track: {track_id} | {info['name']} {info['confidence']:.1f}%"
                cv2.putText(frame, label, (x1, max(y1 - 10, 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            cv2.putText(frame, f"FPS: {current_fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            if self.on_frame_callback:
                # Convert BGR to RGB for GUI display
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.on_frame_callback(rgb_frame)
                
            time.sleep(0.01) # Small sleep to prevent CPU hogging
            
        cap.release()
        if self.on_event_callback:
            self.on_event_callback("Video processing stopped.")
        self.is_running = False
