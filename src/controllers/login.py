from flask import Blueprint, render_template, request, redirect, url_for, flash, session
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
            # Login en Bonita usando OPCIÓN 1
            access_api = AccessAPI()
            bonita_session = access_api.login(username, password)

            # Guardar datos en la sesión de Flask
            session["bonita_username"] = username
            session["bonita_cookies"] = bonita_session.cookies.get_dict()

            flash(f'¡Bienvenido {username}!', 'success')
            return redirect(url_for('formulario.index'))
            
        except Exception as e:
            flash(f'Error de autenticación: {str(e)}', 'error')
            return render_template('login.html')
    
    return render_template('login.html')


@login_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('login.login'))
