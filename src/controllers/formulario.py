from flask import Blueprint, render_template, request, redirect, url_for, flash


# Crear el Blueprint
formulario_bp = Blueprint('formulario', __name__)

@formulario_bp.route('/formulario_nombre', methods=['GET', 'POST'])
def formulario_nombre():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        if nombre:
            # Aquí puedes procesar el nombre como necesites
            flash(f'Formulario enviado correctamente. Nombre: {nombre}', 'success')
            return redirect(url_for('formulario.formulario_nombre'))
        else:
            flash('Por favor, ingresa un nombre válido.', 'error')
    
    return render_template('formulario_nombre.html')
