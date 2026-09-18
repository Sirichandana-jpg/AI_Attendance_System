import cv2
import os
import time
from deepface import DeepFace
from src.database import database
from src.utils.config_manager import get_config_value

def register_student(student_id, student_name, department, num_samples=3):
    # Check if student already exists
    if database.get_student_by_id(student_id):
        print(f"Student with ID {student_id} already exists.")
        return False
        
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Camera unavailable.")
        return False

    folder_path = os.path.join("dataset", f"{student_id}_{student_name.replace(' ', '_')}")
    os.makedirs(folder_path, exist_ok=True)
    
    samples_collected = 0
    embeddings = []
    
    model_name = get_config_value("recognition", "model_name", "Facenet")
    detector_backend = get_config_value("recognition", "detector_backend", "opencv")
    
    print(f"Starting registration for {student_name}. Look at the camera.")
    
    while samples_collected < num_samples:
        ret, frame = camera.read()
        if not ret:
            print("Failed to capture frame.")
            break
            
        display_frame = frame.copy()
        cv2.putText(display_frame, f"Samples: {samples_collected}/{num_samples} - Press 's' to capture", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Student Registration", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            # Save temporary image for DeepFace processing
            temp_path = os.path.join(folder_path, f"temp_{samples_collected}.jpg")
            cv2.imwrite(temp_path, frame)
            
            try:
                # Validate and extract embedding
                res = DeepFace.represent(img_path=temp_path, model_name=model_name, 
                                         enforce_detection=True, detector_backend=detector_backend)
                
                if len(res) == 1:
                    # Exactly one face
                    embedding = res[0]['embedding']
                    embeddings.append(embedding)
                    
                    # Rename to final
                    final_path = os.path.join(folder_path, f"sample_{samples_collected+1}.jpg")
                    os.rename(temp_path, final_path)
                    
                    samples_collected += 1
                    print(f"Sample {samples_collected} collected successfully.")
                else:
                    print("Multiple faces detected. Please ensure only one face is in the frame.")
                    os.remove(temp_path)
            except ValueError:
                print("No face detected or blurry. Try again.")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                print(f"Error extracting embedding: {e}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        elif key == ord('q'):
            print("Registration cancelled by user.")
            break
            
    camera.release()
    cv2.destroyAllWindows()
    
    if samples_collected > 0:
        # Save to DB
        database.add_student(student_id, student_name, department)
        # We save the first embedding (or average) to DB, saving all for now 
        for emb in embeddings:
            database.add_embedding(student_id, emb, model_name)
        print(f"Registration successful for {student_name}.")
        return True
    else:
        print("Registration failed, no samples collected.")
        # Cleanup folder
        try:
            os.rmdir(folder_path)
        except:
            pass
        return False
