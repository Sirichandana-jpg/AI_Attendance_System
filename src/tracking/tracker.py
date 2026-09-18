from ultralytics import YOLO
from src.utils.config_manager import get_config_value

class PersonTracker:
    def __init__(self):
        model_name = get_config_value("detection", "model", "yolov8n.pt")
        self.confidence_threshold = get_config_value("detection", "confidence", 0.5)
        self.model = YOLO(model_name)

    def track(self, frame):
        """
        Track persons in the frame using YOLO's built-in tracker (ByteTrack).
        Returns a list of dictionaries containing tracking information.
        """
        results = self.model.track(frame, conf=self.confidence_threshold, classes=[0], persist=True, tracker="bytetrack.yaml", verbose=False)
        
        tracked_persons = []
        if results and len(results) > 0 and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)
            
            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box
                tracked_persons.append({
                    "track_id": track_id,
                    "bbox": (x1, y1, x2, y2)
                })
                
        return tracked_persons
