from deepface import DeepFace
from src.utils.config_manager import get_config_value

def detect_faces(frame):
    """
    Detect faces in the frame using DeepFace backend.
    Returns a list of dictionaries with bounding box coordinates.
    """
    detector_backend = get_config_value("recognition", "detector_backend", "opencv")
    try:
        faces = DeepFace.extract_faces(img_path=frame, enforce_detection=True, detector_backend=detector_backend)
        return faces
    except ValueError:
        # No face detected
        return []
    except Exception as e:
        print(f"Error in face detection: {e}")
        return []
