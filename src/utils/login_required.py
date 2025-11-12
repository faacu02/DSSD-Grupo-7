from flask import redirect, url_for, flash, session

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged'):
            flash('Por favor, inicia sesión para acceder.', 'error')
            return redirect(url_for('formulario.login'))
        return f(*args, **kwargs)
    return decorated_function