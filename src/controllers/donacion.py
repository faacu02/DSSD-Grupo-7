from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from classes.access import AccessAPI
import time
import json

from controllers import etapa
from services import etapa_service

donacion_bp = Blueprint('donacion', __name__)
@donacion_bp.route('/cargar_donacion', methods=['GET', 'POST'])
def cargar_donacion():
    case_id = request.args.get('case_id')
    etapa_id = request.args.get('etapa_id')
    etapa = etapa_service.obtener_etapa_por_id(etapa_id)
    etapa_cloud_id = etapa.etapa_cloud_id if etapa else None
    if request.method == 'POST':

        donante_nombre = request.form.get('donante_nombre')
        monto = request.form.get('monto')

        # ES LA CLAVE → VIENE COMO JSON STRING DEL FRONT
        especificacion_raw = request.form.get('especificacion')

        # -----------------------------------------
        #   4. Parsear especificación
        # -----------------------------------------
        try:
            especificacion = json.loads(especificacion_raw) if especificacion_raw else None
        except json.JSONDecodeError:
            especificacion = {"detalle": especificacion_raw}

        # -----------------------------------------
        #   5. Convertir monto correctamente
        # -----------------------------------------
        try:
            monto_float = float(monto) if monto else None
        except ValueError:
            flash("El monto debe ser un número válido.", "error")
            return redirect(request.url)

        # -----------------------------------------
        #   6. Armar JSON limpio para Bonita
        # -----------------------------------------
        donacion_data = {
            "case_id": case_id,
            "etapa_id": etapa_cloud_id,
            "monto": monto_float,
            "especificacion": especificacion,
            "donante_nombre": donante_nombre
        }

        print(f"📤 JSON enviado a Bonita:\n{donacion_data}")

        # -----------------------------------------
        #   7. Llamar endpoint interno /bonita/cargar_donacion
        # -----------------------------------------
        try:
            response = requests.post(
                url_for('bonita_siguiente.cargar_donacion', _external=True),
                json=donacion_data
            )

            data = response.json()

            if not data.get("success"):
                flash(f"Error al cargar donación en Bonita: {data.get('error')}", 'error')
            else:
                flash('Donación cargada correctamente.', 'success')
                return redirect(url_for('formulario.index'))

        except Exception as e:
            flash(f'Error al cargar donación: {str(e)}', 'error')

    # -----------------------------------------
    #  GET → Renderizar formulario con params
    # -----------------------------------------
    case_id = request.args.get('case_id')
    etapa_id = request.args.get('etapa_id')

    return render_template('cargar_donacion.html',
                           case_id=case_id,
                           etapa_id=etapa_id, etapa_cloud_id=etapa_cloud_id)

