from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, current_user, logout_user
from app.models import User

import numpy as np
import face_recognition
from app.utils import process_face_encoding
import base64
from werkzeug.security import generate_password_hash


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.get_user(username)
        if user and user.check_password(password):
            login_user(user)
            if not user.face_verified:
                return redirect(url_for('auth.verify_face_route'))  # Redirection vers la vérification faciale
            return redirect(url_for('auth.dashboard'))  # Redirection vers le dashboard si déjà vérifié
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect", "danger")

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username')
    password = request.form.get('password')
    face_image_data = request.form.get('face_data')

    if not username or not password or not face_image_data:
        flash("Tous les champs sont requis.", "error")
        return redirect(url_for("auth.register"))

    # Vérifier si l'utilisateur existe déjà
    if User.get_user(username):
        flash("Ce nom d'utilisateur est déjà pris.", "error")
        return redirect(url_for("auth.register"))

    # 🔹 Traitement de l'encodage facial
    
    face_encoding = process_face_encoding(face_image_data)
    if face_encoding is None:
        flash("Aucun visage détecté.", "error")
        return redirect(url_for("auth.register"))

    # 🔹 Convertir en base64 pour stockage
    face_encoding_bytes = np.array(face_encoding, dtype=np.float64).tobytes()
    face_encoding_b64 = base64.b64encode(face_encoding_bytes).decode('utf-8')

    # 🔹 Créer et enregistrer l'utilisateur
    new_user = User(
        username=username,
        password=generate_password_hash(password),
        face_data=face_encoding_b64  # Stocke en base64
    )
    new_user.save()

    flash("Inscription réussie ! Connecte-toi maintenant.", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route('/')
@login_required
def dashboard():
    if not current_user.face_verified:
        return redirect(url_for('auth.verify_face_route'))  # Redirection vers la page de vérification si non vérifié

    return render_template('dashboard.html', username=current_user.username)


@auth_bp.route('/verify-face', methods=['GET', 'POST'])
@login_required
def verify_face_route():
    if request.method == 'GET':
        return render_template('verify_face.html')

    data = request.get_json()
    face_image_data = data.get('face_data')

    if not face_image_data:
        flash("Aucune image reçue.", "error")
        return redirect(url_for("auth.verify_face_route"))

    captured_face_encoding = process_face_encoding(face_image_data)

    if captured_face_encoding is None:
        flash("Aucun visage détecté.", "error")
        return redirect(url_for("auth.verify_face_route"))

    # 🔹 Récupérer les données faciales de l'utilisateur
    stored_face_encoding = current_user.face_data  # Assure-toi que current_user est bien chargé

    if stored_face_encoding is None:
        flash("Aucune donnée faciale enregistrée.", "error")
        return redirect(url_for("auth.verify_face_route"))

    # 🔹 Vérifier si c'est une chaîne et la convertir en liste de float
    if isinstance(stored_face_encoding, str):
        import ast
        stored_face_encoding = ast.literal_eval(stored_face_encoding)

    # 🔹 Convertir en `numpy array`
    stored_face_encoding = np.array(stored_face_encoding, dtype=np.float64)

    # 🔹 Vérifier si l'encodage du visage correspond
    match = face_recognition.compare_faces([stored_face_encoding], captured_face_encoding)[0]

    if match:
        current_user.face_verified = True
        current_user.save()
        flash("Vérification réussie !", "success")
        return redirect(url_for("auth.dashboard"))
    else:
        flash("Échec de la reconnaissance faciale.", "danger")
        return redirect(url_for("auth.verify_face_route"))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()  
    flash('Déconnexion réussie.', 'success')  
    return redirect(url_for('auth.login'))  # Rediriger vers la page de connexion
