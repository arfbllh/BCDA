import secrets
from datetime import timedelta

from flask import g, request
from flask_restful import Resource

from api.error_response import api_error
from core.datetime_util import utc_now
from extensions import db
from models.invite_code import InviteCode
from routes.auth_guard import require_auth


class InviteCodes(Resource):
    @require_auth
    def post(self):
        if g.current_user.role != "admin":
            return api_error("FORBIDDEN", "Admin role required."), 403
        payload = request.get_json(silent=True) or {}
        code = (payload.get("code") or "").strip() or secrets.token_urlsafe(8).upper()
        max_uses = int(payload.get("max_uses") or 1)
        ttl_days = int(payload.get("ttl_days") or 30)
        row = InviteCode(
            code=code,
            description=(payload.get("description") or "").strip() or None,
            max_uses=max(1, max_uses),
            used_count=0,
            is_active=True,
            expires_at=utc_now() + timedelta(days=max(1, ttl_days)),
        )
        db.session.add(row)
        db.session.commit()
        return {
            "code": row.code,
            "max_uses": row.max_uses,
            "used_count": row.used_count,
            "expires_at": row.expires_at.isoformat() if row.expires_at else None,
        }, 201
