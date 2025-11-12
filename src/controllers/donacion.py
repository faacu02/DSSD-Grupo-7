from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from classes.access import AccessAPI

from formulario import formulario_bp




@formulario_bp.route('/cargar_donacion', methods=['GET', 'POST'])
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