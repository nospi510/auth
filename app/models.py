from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db_connection
import base64
import numpy as np


class User(UserMixin):
    def __init__(self, id, username, password, face_data=None, face_verified=False):
        self.id = id
        self.username = username
        self.password = password
        self.face_data = face_data
        self.face_verified = face_verified  # Champ pour la vérification faciale

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, face_data) VALUES (%s, %s, %s)",
                       (self.username, self.password, self.face_data))
        conn.commit()
        conn.close()
    
    @staticmethod
    def create_user(username, password, face_encoding):
        conn = get_db_connection()
        cursor = conn.cursor()

        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (username, password, face_data) VALUES (%s, %s, %s)",
            (username, hashed_password, face_encoding)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_user(username):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            user = User(**user_data)

            # 🔹 Vérifier si `face_data` existe
            if user.face_data:
                try:
                    # 🔹 Décoder la base64 → bytes
                    face_bytes = base64.b64decode(user.face_data)

                    # 🔹 Vérifier la taille pour éviter `ValueError`
                    if len(face_bytes) % 8 == 0:  # np.float64 = 8 octets
                        user.face_data = np.frombuffer(face_bytes, dtype=np.float64)
                    else:
                        print("⚠️ Warning: face_bytes size incorrect, conversion skipped!")
                        user.face_data = None

                except Exception as e:
                    print(f"❌ Erreur lors de la conversion des données faciales : {e}")
                    user.face_data = None  # Evite une erreur dans le code

            return user
        return None


    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def get_user_by_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return User(user["id"], user["username"], user["password"], user["face_data"], user["face_verified"])
        return None

    def save(self):
        # Méthode pour sauvegarder l'utilisateur dans la base de données, en particulier pour la mise à jour de face_verified
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET face_verified = %s WHERE id = %s",
            (self.face_verified, self.id)
        )
        conn.commit()
        conn.close()
