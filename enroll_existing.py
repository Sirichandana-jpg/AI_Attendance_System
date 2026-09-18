import os
import cv2
from deepface import DeepFace
from src.database import database
from src.utils.config_manager import get_config_value

def enroll_existing():
    dataset_path = "dataset"
    model_name = get_config_value("recognition", "model_name", "Facenet")
    detector_backend = get_config_value("recognition", "detector_backend", "opencv")
    
    for folder in os.listdir(dataset_path):
        folder_path = os.path.join(dataset_path, folder)
        if not os.path.isdir(folder_path):
            continue
            
        parts = folder.split('_', 1)
        if len(parts) == 2:
            student_id = parts[0]
            name = parts[1].replace('_', ' ')
        else:
            student_id = folder
            name = folder
            
        # Check if exists in DB
        if database.get_student_by_id(student_id):
            print(f"Skipping {name} ({student_id}), already in DB.")
            continue
            
        print(f"Enrolling {name} ({student_id})...")
        
        embeddings = []
        for file in os.listdir(folder_path):
            if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
                
            img_path = os.path.join(folder_path, file)
            try:
                res = DeepFace.represent(img_path=img_path, model_name=model_name, 
                                         enforce_detection=True, detector_backend=detector_backend)
                if len(res) == 1:
                    embeddings.append(res[0]['embedding'])
            except Exception as e:
                print(f"Failed to extract from {img_path}: {e}")
                
        if len(embeddings) > 0:
            database.add_student(student_id, name, "Unknown")
            for emb in embeddings:
                database.add_embedding(student_id, emb, model_name)
            print(f"Successfully enrolled {name} with {len(embeddings)} embeddings.")
        else:
            print(f"Failed to enroll {name}, no valid faces found.")

if __name__ == "__main__":
    database.initialize_database()
    enroll_existing()
