import face_recognition
import os
import shutil

input_dir = "my_photos"
output_dir = "sorted_faces"
known_encodings = []

for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join(input_dir, filename)

        # Load and encode the face
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)

        if not encodings:
            continue  # Skip if no face found

        current_face = encodings[0]
        match_index = None

        # Compare with faces we already know
        results = face_recognition.compare_faces(known_encodings, current_face, tolerance=0.6)

        if True in results:
            match_index = results.index(True)
        else:
            known_encodings.append(current_face)
            match_index = len(known_encodings) - 1

        # Move to folder
        person_folder = os.path.join(output_dir, f"Person_{match_index + 1}")
        os.makedirs(person_folder, exist_ok=True)
        shutil.copy(path, os.path.join(person_folder, filename))