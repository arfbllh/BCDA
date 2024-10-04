import secrets
from datetime import timedelta

from flask import g, request
from werkzeug.security import check_password_hash, generate_password_hash

from core.datetime_util import utc_now
from extensions import db
from models.auth_session import AuthSession
from models.invite_code import InviteCode
from models.user import User


class AuthError(Exception):
    pass


class AuthService:
    session_ttl_hours = 24 * 7

    def signup(self, email: str, full_name: str, password: str, invite_code: str) -> User:
        invite = InviteCode.query.filter_by(code=invite_code).first()
        if invite is None or not invite.is_active:
            raise AuthError("Invite code is invalid.")
        if invite.expires_at and invite.expires_at < utc_now():
            raise AuthError("Invite code has expired.")
        if invite.used_count >= invite.max_uses:
            raise AuthError("Invite code usage limit reached.")
        if User.query.filter_by(email=email.lower().strip()).first() is not None:
            raise AuthError("Email already exists.")

        user = User(
            email=email.lower().strip(),
            full_name=full_name.strip(),
            password_hash=generate_password_hash(password),
            role="user",
            status="active",
        )
        invite.used_count += 1
        db.session.add(user)
        db.session.commit()
        return user

    def login(self, email: str, password: str) -> tuple[User, AuthSession]:
        user = User.query.filter_by(email=email.lower().strip()).first()
        if user is None or not check_password_hash(user.password_hash, password):
            raise AuthError("Invalid email or password.")
        if user.status != "active":
            raise AuthError("Your account is not active.")
        token = secrets.token_urlsafe(48)
        session = AuthSession(
            token=token,
            user_id=user.id,
            expires_at=utc_now() + timedelta(hours=self.session_ttl_hours),
        )
        db.session.add(session)
        db.session.commit()
        return user, session

    def logout(self, token: str) -> None:
        session = AuthSession.query.filter_by(token=token).first()
        if session is None:
            return
        session.revoked_at = utc_now()
        db.session.commit()

    def get_user_by_token(self, token: str) -> User | None:
        if not token:
            return None
        session = AuthSession.query.filter_by(token=token).first()
        if session is None:
            return None
        if session.revoked_at is not None or session.expires_at <= utc_now():
            return None
        return User.query.filter_by(id=session.user_id).first()

    def token_from_request(self) -> str | None:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth.replace("Bearer ", "", 1).strip()
        return None

    def attach_request_user(self) -> None:
        token = self.token_from_request()
        g.current_user = self.get_user_by_token(token) if token else None
