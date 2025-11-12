from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from classes.access import AccessAPI
import time

donacion_bp = Blueprint('donacion', __name__)
@donacion_bp.route('/cargar_donacion', methods=['GET', 'POST'])
def cargar_donacion():
    if request.method == 'POST':
        case_id = request.args.get('case_id')
        print(f"🔍 case_id recibido en cargar_donacion: {case_id}")
        etapa_id = request.args.get('etapa_id')
        if case_id:
            try:
                response = requests.post(
                    url_for('bonita_siguiente.completar_seleccionar_etapa', _external=True),
                    json={"case_id": case_id}
                )
                data = response.json()
                if not data.get("success"):
                    print(f"⚠️ Bonita devolvió error al completar 'Seleccionar etapa': {data.get('error')}")
                else:
                    print(f"✅ Tarea 'Seleccionar etapa' completada para case {case_id}")
            except Exception as e:
                print(f"⚠️ Error de conexión al completar 'Seleccionar etapa': {e}")
        else:
            print("⚠️ No se recibió case_id, no se completó tarea en Bonita.")
        donante_nombre = request.form.get('donante_nombre')
        monto = request.form.get('monto')
        especificacion = request.form.get('especificacion')

        try:
            # Convertir monto a float si existe
            monto_float = float(monto) if monto else None
            
            # Preparar datos de la donación
            donacion_data = {
                'etapa_id': etapa_id,
                'monto': monto_float if monto_float is not None else None,
                'especificacion': especificacion if especificacion else None,
                'donante_nombre': donante_nombre if donante_nombre else None,
                'case_id': case_id  
            }
            for i in range(10):  # máximo 10 intentos (10 segundos)
                check = requests.get(
                    f"http://localhost:8080/bonita/API/bpm/activity?f=caseId={case_id}&f=name=Proponer%20donación"
                )
                if check.status_code == 200:
                    actividades = check.json()
                    if actividades and actividades[0].get("state") in ["ready", "executing"]:
                        print(f"✅ Tarea 'Proponer donación' ya está disponible (estado: {actividades[0]['state']})")
                        break
                print(f"⌛ Esperando que 'Proponer donación' se cree... ({i+1}/10)")
                time.sleep(1)
            else:
                print("⚠️ La tarea 'Proponer donación' nunca estuvo lista, se intentará de todos modos.")

            # Ahora sí, ejecutar el endpoint que la completa
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
            
        except ValueError:
            flash('El monto debe ser un número válido.', 'error')
        except Exception as e:
            flash(f'Error al cargar donación: {str(e)}', 'error')

    return render_template('cargar_donacion.html')