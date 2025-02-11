from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db_connection
import base64


class User(UserMixin):
    def __init__(self, id, username, password, face_data, face_verified=False):
        self.id = id
        self.username = username
        self.password = password
        self.face_data = face_data
        self.face_verified = face_verified  # Champ pour la vérification faciale

    @staticmethod
    def create_user(username, password, face_data):
        conn = get_db_connection()
        cursor = conn.cursor()

        # 🔹 Hasher le mot de passe
        hashed_password = generate_password_hash(password)

        # 🔹 Encoder face_data en base64 + utf-8
        face_data_encoded = base64.b64encode(face_data.encode('utf-8')).decode('utf-8')

        cursor.execute(
            "INSERT INTO users (username, password, face_data) VALUES (%s, %s, %s)",
            (username, hashed_password, face_data_encoded)
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
            # Créer une instance de User avec les données récupérées
            user = User(**user_data)
            # Décoder 'face_data' si nécessaire
            if user.face_data:
                user.face_data = base64.b64decode(user.face_data).decode('utf-8')
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
