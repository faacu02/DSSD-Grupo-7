from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
import services.proyecto_servicce as proyecto_service
import services.etapa_service as etapa_service
from datetime import datetime
from classes.access import AccessAPI
from utils.login_required import login_required

# Crear el Blueprint
formulario_bp = Blueprint('formulario', __name__)



@formulario_bp.route('/')
def root():
    """Ruta raíz - redirige al login o al index según el estado de sesión"""
    if session.get('logged'):
        return redirect(url_for('formulario.index'))
    return redirect(url_for('formulario.login'))

@formulario_bp.route('/index')
@login_required
def index():
    """Página de inicio de ProjectPlanning"""
    return render_template('index.html')


def to_timestamp(fecha_str):
    if not fecha_str:
        return None
    dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)

@formulario_bp.route('/formulario_nombre', methods=['GET', 'POST'])
@login_required
def formulario_nombre():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        if nombre:
            try:
                proyecto = proyecto_service.crear_proyecto(nombre)
                response = requests.post(
                    url_for('bonita.completar_actividad', _external=True),
                    json={"nombre": nombre,"proyecto_id": proyecto.id}
                )
                data = response.json()
                if data.get("success"):
                    # Obtener el case_id del resultado
                    case_id = data["result"].get("caseId") if data.get("result") else None
                    flash(f'Proyecto creado correctamente. Nombre: {nombre}', 'success')
                    if case_id:
                        # Redirigir a cargar_etapa y pasar el case_id y proyecto_id por la URL
                        return redirect(url_for('etapa.cargar_etapa', case_id=case_id, proyecto_id=proyecto.id))
                    flash(f'Proyecto creado correctamente. Nombre: {nombre}', 'success')
                else:
                    flash(f'Error al crear proyecto: {data.get("error")}', 'error')
            except Exception as e:
                flash(f'Error de conexión: {str(e)}', 'error')
            return redirect(url_for('formulario.formulario_nombre'))
        else:
            flash('Por favor, ingresa un nombre válido.', 'error')
    # Obtener case_id y proyecto_id de la URL si existen y pasarlos al template
    case_id = request.args.get('case_id')
    return render_template('formulario_nombre.html', case_id=case_id)


@formulario_bp.route('/confirmar_proyecto', methods=['GET', 'POST'])
@login_required
def confirmar_proyecto():
    case_id = request.args.get('case_id')
    proyecto_id = request.args.get('proyecto_id')
    if request.method == 'POST':
        try:
            response = requests.post(
                url_for('bonita_siguiente.confirmar_proyecto', _external=True),
                json={"case_id": case_id, "ultima_etapa": True}
            )
            data = response.json()
            if data.get("success"):
                flash('Proyecto confirmado correctamente.', 'success')
                return redirect(url_for('formulario.formulario_nombre'))
            else:
                flash(f'Error al confirmar: {data.get("error")}', 'error')
        except Exception as e:
            flash(f'Error de conexión: {str(e)}', 'error')

    return render_template('confirmar_proyecto.html',
                           case_id=case_id,
                           proyecto_id=proyecto_id)

@formulario_bp.route('/cargar_donacion', methods=['GET', 'POST'])
@login_required
def cargar_donacion():
    if request.method == 'POST':
        donante_nombre = request.form.get('donante_nombre')
        monto = request.form.get('monto')
        especificacion = request.form.get('especificacion')

        try:
            # Convertir monto a float si existe
            monto_float = float(monto) if monto else None
            
            # Preparar datos de la donación
            donacion_data = {
                'donante_nombre': donante_nombre if donante_nombre else None,
                'monto': monto_float,
                'especificacion': especificacion if especificacion else None
            }

            # Aquí puedes enviar los datos a Bonita o procesarlos según necesites
            # Por ejemplo:
            # response = requests.post(
            #     url_for('bonita.procesar_donacion', _external=True),
            #     json=donacion_data
            # )
            # data = response.json()
            
            flash('Donación cargada correctamente.', 'success')
            return redirect(url_for('formulario.index'))
            
        except ValueError:
            flash('El monto debe ser un número válido.', 'error')
        except Exception as e:
            flash(f'Error al cargar donación: {str(e)}', 'error')

    return render_template('cargar_donacion.html')

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

