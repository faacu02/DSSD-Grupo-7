from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from classes.access import AccessAPI
import services.proyecto_servicce as proyecto_service
from classes.process import Process

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
            # Login en Bonita
            access_api = AccessAPI()
            bonita_session = access_api.login(username, password)

            # Guardar cookies
            session["bonita_username"] = username
            session["bonita_cookies"] = bonita_session.cookies.get_dict()

            # Inicializar Process con la sesión correcta
            process = Process(bonita_session)

            # 🔥 Buscar el usuario por nombre
            bonita_user = process.get_user_by_name(username)
            if not bonita_user:
                raise Exception("Usuario no encontrado en Bonita")

            user_id = bonita_user.get("id")

            # 🔥 Obtener roles por ID
            roles = process.get_user_roles_names(user_id)

            # Guardar en la session
            session["bonita_roles"] = roles
            session["bonita_user_id"] = user_id
            if proyecto_service.hay_proyectos():
                case_id = proyecto_service.devolver_case_id_por_proyecto_id()
            else:
                case_id = None
            print("Usuario:", username)
            print("User ID:", user_id)
            print("Roles:", roles)

            flash(f'¡Bienvenido {username}!', 'success')
            return redirect(url_for('formulario.index', case_id=case_id))
            
        except Exception as e:
            flash(f'Error de autenticación: {str(e)}', 'error')
            return render_template('login.html')
    
    return render_template('login.html')




@login_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('login.login'))
