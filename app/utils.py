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


def get_face_data(username):
    """ Récupère les données faciales stockées en base de données """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT face_data FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and user["face_data"]:
        # Convertir les données en tableau numpy
        try:
            return np.frombuffer(user["face_data"].encode('utf-8'), dtype=np.float64)
        except ValueError:
            print("❌ Erreur : Données faciales corrompues.")
            return None
    return None

def process_face_encoding(image_base64):
    """ Convertir une image base64 en encodage faciale. """
    try:
        # 🔹 Décoder l’image base64
        image_data = base64.b64decode(image_base64.split(",")[1])
        np_arr = np.frombuffer(image_data, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # 🔹 Convertir BGR → RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 🔹 Détecter et encoder le visage
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            return None

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        return face_encodings[0] if face_encodings else None

    except Exception as e:
        print(f"Erreur encodage faciale : {e}")
        return None


def verify_face(username=None):
    """ Compare le visage capturé avec celui enregistré en base """
    if username is None:
        username = current_user.username

    stored_face_encoding = get_face_data(username)

    if stored_face_encoding is None:
        return False, "Aucune donnée faciale enregistrée."

    captured_face_encoding = capture_face()
    if captured_face_encoding is None:
        return False, "Aucun visage détecté pendant la capture."

    # Comparaison des visages
    matches = face_recognition.compare_faces([stored_face_encoding], captured_face_encoding)

    return (True, "Reconnaissance faciale réussie!") if matches[0] else (False, "Échec de la reconnaissance faciale.")
