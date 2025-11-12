from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
import services.etapa_service as etapa_service


etapa_bp = Blueprint('etapa', __name__)

@etapa_bp.route('/completar_etapa', methods=['GET', 'POST'])
def cargar_etapa():
    if request.method == 'POST':
        case_id = request.form.get('case_id')
        proyecto_id = request.form.get('proyecto_id')
        nombre_etapa = request.form.get('nombre_etapa')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        tipo_cobertura = request.form.get('tipo_cobertura')
        cobertura_solicitada = request.form.get('cobertura_solicitada')

        # ✅ convertir checkbox a boolean real
        ultima_etapa = request.form.get('ultima_etapa')

        if proyecto_id and nombre_etapa and fecha_inicio and fecha_fin and tipo_cobertura and cobertura_solicitada:
            try:
                etapa_service.crear_etapa(
                    nombre_etapa,
                    fecha_inicio,
                    fecha_fin,
                    tipo_cobertura,
                    cobertura_solicitada,
                    int(proyecto_id)
                )

                # Enviar datos a Bonita (incluyendo ultima_etapa como bool real)
                response = requests.post(
                    url_for('bonita_siguiente.cargar_etapa', _external=True),
                    json={
                        "case_id": case_id,
                        "nombre_etapa": nombre_etapa,
                        "proyecto_id": proyecto_id,
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "tipo_cobertura": tipo_cobertura,
                        "cobertura_solicitada": cobertura_solicitada,
                        "ultima_etapa": ultima_etapa
                    }
                )
                data = response.json()
                if data.get("success"):
                    flash(f'Etapa cargada correctamente para el caso {case_id}', 'success')
                else:
                    flash(f'Error al cargar etapa: {data.get("error")}', 'error')

            except Exception as e:
                flash(f'Error de conexión: {str(e)}', 'error')

            if ultima_etapa == 'true':
                return redirect(url_for('formulario.confirmar_proyecto',
                                        case_id=case_id,
                                        proyecto_id=proyecto_id))

            # ✅ Si no es última, volver al mismo formulario para seguir cargando
            return redirect(url_for('etapa.cargar_etapa',
                                    case_id=case_id,
                                    proyecto_id=proyecto_id))
        else:
            flash('Por favor, completa todos los campos.', 'error')

    # GET → renderizar formulario vacío o con case_id/proyecto_id
    case_id = request.args.get('case_id')
    proyecto_id = request.args.get('proyecto_id')
    return render_template('cargar_etapa.html',
                           case_id=case_id,
                           proyecto_id=proyecto_id)