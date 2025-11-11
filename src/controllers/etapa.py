from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
import services.etapa_service as etapa_service
from datetime import datetime

# Crear el Blueprint
etapa_bp = Blueprint('etapa', __name__)

@etapa_bp.route('/cargar', methods=['GET', 'POST'])
def cargar_etapa():
    if request.method == 'POST':
        proyecto_id = request.form.get('proyecto_id')
        nombre = request.form.get('nombre_etapa')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        tipo_cobertura = request.form.get('tipo_cobertura')
        cobertura_solicitada = request.form.get('cobertura_solicitada')

        descripcion = request.form.get('descripcion_etapa')
        
        etapa_service.crear_etapa(nombre, descripcion, fecha_inicio, fecha_fin)


    return render_template('cargar_etapa.html')