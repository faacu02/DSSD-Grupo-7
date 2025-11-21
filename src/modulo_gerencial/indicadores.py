# routes/indicadores.py

from flask import Blueprint, jsonify, render_template
from datetime import date
from db import db
from models.proyecto import Proyecto
from models.etapa import Etapa

from modulo_gerencial.bonita_utils import (
    get_process_id_by_name,
    obtener_casos_completados
)

indicadores_bp = Blueprint("indicadores", __name__)


@indicadores_bp.route("/proyectos-en-termino", methods=["GET"])
def indicador_proyectos_en_termino():
    """
    INDICADOR 1:
    Porcentaje de proyectos finalizados en término.

    BONITA:
        - end_date de los casos completados
        - state = completed
    BD LOCAL:
        - fecha_fin de la última etapa del proyecto (planificada)
    """

    # 1) Nombre EXACTO del proceso en Bonita
    process_name = "Proceso de generar proyecto"

    # 2) Obtener el processId automáticamente
    try:
        process_id = get_process_id_by_name(process_name)
    except Exception as e:
        return {"error": f"No pudo obtener processId: {str(e)}"}, 500

    # 3) Obtener todos los casos completados del proceso
    try:
        casos = obtener_casos_completados(process_id)
    except Exception as e:
        return {"error": f"No pudo obtener casos completados: {str(e)}"}, 500

    total = 0
    en_termino = 0

    for caso in casos:
        print("\n================= NUEVO CASO =================")
        
        case_id = int(caso.get("sourceObjectId", -1))
        print("Case ID Bonita:", case_id)

        proyecto = Proyecto.query.filter_by(case_id=case_id).first()
        print("Proyecto encontrado:", proyecto.id if proyecto else None, proyecto.nombre if proyecto else None)

        if not proyecto:
            print("❌ No existe proyecto con este case_id en la BD")
            continue

        end_date_str = caso.get("end_date") or caso.get("endDate")
        print("Raw end_date_str:", end_date_str)

        if not end_date_str:
            print("❌ Caso sin end_date")
            continue

        try:
            fecha_fin_real = date.fromisoformat(end_date_str[:10])
        except:
            print("❌ Error convirtiendo end_date")
            continue

        print("➡ Fecha fin REAL (Bonita):", fecha_fin_real)

        # Etapas
        etapas = Etapa.query.filter_by(proyecto_id=proyecto.id).all()
        print("Etapas del proyecto:")
        for e in etapas:
            print("  Etapa:", e.id, "inicio:", e.fecha_inicio, "fin:", e.fecha_fin)

        etapa_final = (
            Etapa.query.filter_by(proyecto_id=proyecto.id)
            .order_by(Etapa.fecha_fin.desc())
            .first()
        )

        if not etapa_final:
            print("❌ Proyecto sin etapas, no se puede evaluar")
            continue

        print("➡ Fecha FIN PLANIFICADA (última etapa):", etapa_final.fecha_fin)

        total += 1

        if fecha_fin_real <= etapa_final.fecha_fin:
            print("✔ EN TÉRMINO")
            en_termino += 1
        else:
            print("❌ FUERA DE TÉRMINO")

    porcentaje = en_termino / total if total > 0 else 0.0

    return jsonify({
        "total_proyectos_evaluados": total,
        "proyectos_en_termino": en_termino,
        "porcentaje_en_termino": porcentaje
    })
    
@indicadores_bp.route("/metricas")
def metricas():
    return render_template("metricas.html")


@indicadores_bp.route("/proyectos-en-termino/vista")
def vista_proyectos_en_termino():
    datos = indicador_proyectos_en_termino().json
    return render_template("proyectos_en_termino.html", datos=datos)


@indicadores_bp.route("/proyectos-no-en-termino", methods=["GET"])
def indicador_proyectos_no_en_termino():
    """
    INDICADOR 1:
    Porcentaje de proyectos finalizados en término.

    BONITA:
        - end_date de los casos completados
        - state = completed
    BD LOCAL:
        - fecha_fin de la última etapa del proyecto (planificada)
    """

    # 1) Nombre EXACTO del proceso en Bonita
    process_name = "Proceso de generar proyecto"

    # 2) Obtener el processId automáticamente
    try:
        process_id = get_process_id_by_name(process_name)
    except Exception as e:
        return {"error": f"No pudo obtener processId: {str(e)}"}, 500

    # 3) Obtener todos los casos completados del proceso
    try:
        casos = obtener_casos_completados(process_id)
    except Exception as e:
        return {"error": f"No pudo obtener casos completados: {str(e)}"}, 500

    total = 0
    no_en_termino = 0

    for caso in casos:
        print("\n================= NUEVO CASO =================")
        
        case_id = int(caso.get("sourceObjectId", -1))
        print("Case ID Bonita:", case_id)

        proyecto = Proyecto.query.filter_by(case_id=case_id).first()
        print("Proyecto encontrado:", proyecto.id if proyecto else None, proyecto.nombre if proyecto else None)

        if not proyecto:
            print("❌ No existe proyecto con este case_id en la BD")
            continue

        end_date_str = caso.get("end_date") or caso.get("endDate")
        print("Raw end_date_str:", end_date_str)

        if not end_date_str:
            print("❌ Caso sin end_date")
            continue

        try:
            fecha_fin_real = date.fromisoformat(end_date_str[:10])
        except:
            print("❌ Error convirtiendo end_date")
            continue

        print("➡ Fecha fin REAL (Bonita):", fecha_fin_real)

        # Etapas
        etapas = Etapa.query.filter_by(proyecto_id=proyecto.id).all()
        print("Etapas del proyecto:")
        for e in etapas:
            print("  Etapa:", e.id, "inicio:", e.fecha_inicio, "fin:", e.fecha_fin)

        etapa_final = (
            Etapa.query.filter_by(proyecto_id=proyecto.id)
            .order_by(Etapa.fecha_fin.desc())
            .first()
        )

        if not etapa_final:
            print("❌ Proyecto sin etapas, no se puede evaluar")
            continue

        print("➡ Fecha FIN PLANIFICADA (última etapa):", etapa_final.fecha_fin)

        total += 1

        if fecha_fin_real > etapa_final.fecha_fin:
            print("❌ FUERA DE TÉRMINO")
            no_en_termino += 1
        else:
            print("❌ FUERA DE TÉRMINO")

    porcentaje = no_en_termino / total if total > 0 else 0.0
    return jsonify({
        "total_proyectos_evaluados": total,
        "proyectos_no_en_termino": no_en_termino,
        "porcentaje_no_en_termino": porcentaje
    })
    
@indicadores_bp.route("/proyectos-no-en-termino/vista")
def vista_proyectos_no_en_termino():
    datos = indicador_proyectos_no_en_termino().json
    return render_template("proyectos_no_en_termino.html", datos=datos)
    

