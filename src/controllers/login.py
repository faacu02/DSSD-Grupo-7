from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required
import requests
from classes.access import AccessAPI

from formulario import formulario_bp


@formulario_bp.route('/login', methods=['GET', 'POST'])
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
            token, bonita_session = access_api.login()
            
            # Si llegamos aquí, el login fue exitoso
            flash(f'¡Bienvenido {username}!', 'success')
            return redirect(url_for('formulario.index'))
            
        except Exception as e:
            flash(f'Error de autenticación: {str(e)}', 'error')
            return render_template('login.html')
    
    # GET - mostrar formulario de login
    return render_template('login.html')

@formulario_bp.route('/logout')
@login_required
def logout():
    # Limpiar la sesión de Flask
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('formulario.login'))
    