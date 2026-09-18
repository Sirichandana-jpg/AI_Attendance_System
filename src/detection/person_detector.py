from ultralytics import YOLO
from src.utils.config_manager import get_config_value

class PersonDetector:
    def __init__(self):
        model_name = get_config_value("detection", "model", "yolov8n.pt")
        self.confidence_threshold = get_config_value("detection", "confidence", 0.5)
        self.model = YOLO(model_name)

    def detect(self, frame):
        """
        Detect persons in the frame.
        Returns a list of bounding boxes [x1, y1, x2, y2] for detected persons.
        """
        results = self.model.predict(frame, conf=self.confidence_threshold, classes=[0], verbose=False)
        boxes = []
        if results and len(results) > 0:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                boxes.append([x1, y1, x2, y2])
        return boxes
