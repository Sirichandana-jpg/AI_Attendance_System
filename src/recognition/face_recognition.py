from deepface import DeepFace
from src.database import database
from src.utils.config_manager import get_config_value
from src.recognition.embeddings import cosine_distance

class FaceRecognizer:
    def __init__(self):
        self.model_name = get_config_value("recognition", "model_name", "Facenet")
        self.detector_backend = get_config_value("recognition", "detector_backend", "opencv")
        self.threshold = get_config_value("recognition", "threshold", 0.40)
        
        # Load all registered embeddings from database
        self.registered_embeddings = database.get_all_embeddings()
        
    def reload_embeddings(self):
        self.registered_embeddings = database.get_all_embeddings()

    def recognize(self, face_image):
        """
        Recognize a face image against stored embeddings.
        Returns (student_id, student_name, confidence) or ("Unknown", "Unknown", 0.0)
        """
        try:
            # Extract embedding for the incoming face
            res = DeepFace.represent(img_path=face_image, model_name=self.model_name, 
                                     enforce_detection=True, detector_backend=self.detector_backend)
            
            if len(res) == 0:
                return "Unknown", "Unknown", 0.0
                
            test_embedding = res[0]['embedding']
            
            best_match = None
            min_distance = float('inf')
            
            for reg in self.registered_embeddings:
                if reg['model_name'] != self.model_name:
                    continue # Skip if model doesn't match
                    
                dist = cosine_distance(reg['embedding'], test_embedding)
                if dist < min_distance:
                    min_distance = dist
                    best_match = reg
                    
            if min_distance <= self.threshold and best_match:
                # Get student details
                student = database.get_student_by_id(best_match['student_id'])
                if student:
                    # Convert distance to a pseudo-confidence percentage (0 to 100%)
                    # For cosine distance, 0 is perfect match, threshold is max allowed.
                    confidence = max(0.0, 1.0 - (min_distance / max(self.threshold, 0.001))) * 100
                    return student['student_id'], student['name'], confidence
            
            return "Unknown", "Unknown", 0.0
            
        except Exception as e:
            print(f"Recognition Error: {e}")
            return "Unknown", "Unknown", 0.0
