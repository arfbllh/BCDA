from functools import wraps

from flask import g

from api.error_response import api_error
from services.auth_service import AuthService


def require_auth(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        auth = AuthService()
        auth.attach_request_user()
        if getattr(g, "current_user", None) is None:
            return api_error("UNAUTHORIZED", "Authentication required."), 401
        return fn(*args, **kwargs)

    return wrapped
