from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from classes.access import AccessAPI

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Por favor ingresa usuario y contraseña.', 'error')
            return render_template('login.html')

        try:
            # Login REAL en Bonita con user/password del formulario
            api = AccessAPI()
            bonita_cookies = api.login(username, password)

            # Guardar sesión por USUARIO
            session["bonita_username"] = username
            session["bonita_cookies"] = bonita_cookies
            print(session)

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
