from functools import wraps
from flask import request, jsonify, session
from itsdangerous import URLSafeSerializer, BadSignature
from config import SECRET_KEY

signer = URLSafeSerializer(SECRET_KEY)


def get_user_id_from_cookie():
    token = request.cookies.get("ballot_token")
    if not token:
        return None
    try:
        data = signer.loads(token)
        return data.get("user_id")
    except BadSignature:
        return None


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
