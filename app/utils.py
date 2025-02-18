import cv2
import numpy as np
import face_recognition
from app.database import get_db_connection
from app.models import User
from flask_login import current_user
import base64

def open_camera():
    """ Ouvre la caméra en testant plusieurs index possibles """
    for index in range(3):  # Tester /dev/video0, /dev/video1, /dev/video2
        video_capture = cv2.VideoCapture(index)
        if video_capture.isOpened():
            print(f"✅ Caméra ouverte sur l'index {index}")
            return video_capture
    print("❌ Erreur : Impossible d'ouvrir la caméra.")
    return None

def capture_face():
    """ Détecte un visage et capture son encodage si un visage est trouvé. """
    video_capture = open_camera()
    if video_capture is None:
        return None

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("❌ Erreur : Impossible de capturer l'image.")
            break

        # Convertir l'image en RGB pour face_recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Détection des visages
        face_locations = face_recognition.face_locations(rgb_frame)

        # Afficher un cadre autour des visages détectés
        for top, right, bottom, left in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)  # Rectangle vert

        cv2.imshow("Détection du Visage", frame)

        if face_locations:
            print("✅ Visage détecté, capture en cours...")
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            video_capture.release()
            cv2.destroyAllWindows()
            return face_encodings[0]  # Retourne l'encodage du premier visage détecté

        # Quitter avec 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return None


def process_face_encoding(face_data):
    """ Convertit une image base64 en encodage facial """
    try:
        # 🔹 Décoder l'image base64 en bytes
        img_bytes = base64.b64decode(face_data)

        # 🔹 Convertir en numpy array
        np_arr = np.frombuffer(img_bytes, dtype=np.uint8)

        # 🔹 Lire l'image avec OpenCV
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            print("❌ Impossible de décoder l'image")
            return None

        # 🔹 Convertir BGR (OpenCV) → RGB (face_recognition)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # 🔹 Détecter les visages et extraire l'encodage
        face_encodings = face_recognition.face_encodings(img_rgb)

        if len(face_encodings) > 0:
            return face_encodings[0]  # Retourne le premier encodage facial
        else:
            print("❌ Aucun visage détecté")
            return None
    except Exception as e:
        print(f"❌ Erreur encodage facial: {e}")
        return None


def get_face_data(username):
    """ Récupère les données faciales d’un utilisateur enregistré """
    user = User.query.filter_by(username=username).first()
    if user and user.face_data:
        return np.array(eval(user.face_data))  # Convertir string en array
    return None