from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from classes.access import AccessAPI

login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor, ingresa usuario y contraseña.', 'error')
            return render_template('login.html')
        
        try:
            # Crear instancia de AccessAPI con las credenciales del formulario
            access_api = AccessAPI()
            access_api.user = username
            access_api.password = password
            
            # Intentar hacer login
            bonita_session = access_api.login()
            # Si llegamos aquí, el login fue exitoso
            flash(f'¡Bienvenido {username}!', 'success')
            return redirect(url_for('formulario.index'))
            
        except Exception as e:
            flash(f'Error de autenticación: {str(e)}', 'error')
            return render_template('login.html')
    
    # GET - mostrar formulario de login
    return render_template('login.html')

@login_bp.route('/logout')
def logout():
    # Limpiar la sesión de Flask
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('login.login'))
    