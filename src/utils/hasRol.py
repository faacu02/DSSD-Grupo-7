from functools import wraps
from flask import session, redirect, url_for, flash

from functools import wraps
from flask import session, redirect, url_for, flash

def roles_required(*required_roles):
    """
    Decorador para restringir acceso por rol.
    Ejemplos:
    @roles_required("Originante")
    @roles_required("Interviniente", "Originante")
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            roles_in_session = session.get("bonita_roles", [])

            if not roles_in_session:
                flash("No tienes roles asignados o tu sesión expiró.", "error")
                return redirect(url_for("login.login"))

            # Normalizamos toda comparación en minúsculas
            roles_in_session = [r.lower() for r in roles_in_session]
            required = [r.lower() for r in required_roles]

            # Verificar si alguno de los roles requeridos coincide
            allowed = any(req_role in roles_in_session for req_role in required)

            if not allowed:
                flash("No tienes permisos para acceder a esta sección.", "error")
                return redirect(url_for("formulario.index"))

            return f(*args, **kwargs)
        return wrapper
    return decorator

