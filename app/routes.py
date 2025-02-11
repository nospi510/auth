from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from app.models import User

import numpy as np
from app.utils import verify_face
import face_recognition
from app.utils import process_face_encoding, get_face_data


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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        face_data = request.form['face_data']  # Image encodée en base64

        # Vérifier si l'utilisateur existe déjà
        if User.get_user(username):
            flash('Nom d\'utilisateur déjà pris.', 'error')
            return redirect(url_for('auth.register'))

        # Créer l'utilisateur avec encodage base64
        User.create_user(username, password, face_data)

        flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/')
@login_required
def dashboard():
    if not current_user.face_verified:
        return redirect(url_for('auth.verify_face_route'))  # Redirection vers la page de vérification si non vérifié

    return render_template('dashboard.html', username=current_user.username)


@auth_bp.route('/verify-face', methods=['GET', 'POST'])
@login_required
def verify_face_route():
    # Si la requête est GET, on rend le template pour la vérification faciale
    if request.method == 'GET':
        return render_template('verify_face.html')

    # Si la requête est POST, on traite la soumission du formulaire
    face_image_data = request.form['face_data']  # Image capturée en JSON

    if not face_image_data:
        flash("Aucune image reçue.", "error")
        return redirect(url_for("auth.verify_face_route"))

    # 🔹 Convertir l'image base64 en encodage de visage
    captured_face_encoding = process_face_encoding(face_image_data)

    if captured_face_encoding is None:
        flash("Aucun visage détecté.", "error")
        return redirect(url_for("auth.verify_face_route"))

    # 🔹 Récupérer l'encodage du visage enregistré
    stored_face_encoding = get_face_data(current_user.username)

    if stored_face_encoding is None:
        flash("Aucune donnée faciale enregistrée.", "error")
        return redirect(url_for("auth.verify_face_route"))

    # 🔹 Comparaison des encodages
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
