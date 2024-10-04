from flask import g, request
from flask_restful import Resource

from api.error_response import api_error
from services.auth_service import AuthError, AuthService


class Signup(Resource):
    def __init__(self):
        self.auth = AuthService()

    def post(self):
        payload = request.get_json(silent=True) or {}
        email = (payload.get("email") or "").strip()
        full_name = (payload.get("full_name") or "").strip()
        password = payload.get("password") or ""
        invite_code = (payload.get("invite_code") or "").strip()
        if not email or not full_name or not password or not invite_code:
            return api_error("VALIDATION_ERROR", "email, full_name, password, invite_code are required."), 400
        try:
            user = self.auth.signup(email, full_name, password, invite_code)
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                }
            }, 201
        except AuthError as exc:
            return api_error("AUTH_ERROR", str(exc)), 400


class Login(Resource):
    def __init__(self):
        self.auth = AuthService()

    def post(self):
        payload = request.get_json(silent=True) or {}
        email = (payload.get("email") or "").strip()
        password = payload.get("password") or ""
        if not email or not password:
            return api_error("VALIDATION_ERROR", "email and password are required."), 400
        try:
            user, session = self.auth.login(email, password)
            return {
                "token": session.token,
                "expires_at": session.expires_at.isoformat(),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                },
            }, 200
        except AuthError as exc:
            return api_error("AUTH_ERROR", str(exc)), 401


class Logout(Resource):
    def __init__(self):
        self.auth = AuthService()

    def post(self):
        token = self.auth.token_from_request()
        if token:
            self.auth.logout(token)
        return {"status": "ok"}, 200


class Me(Resource):
    def __init__(self):
        self.auth = AuthService()

    def get(self):
        self.auth.attach_request_user()
        user = getattr(g, "current_user", None)
        if user is None:
            return api_error("UNAUTHORIZED", "Authentication required."), 401
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "status": user.status,
        }, 200
