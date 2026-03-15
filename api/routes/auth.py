from flask import Blueprint, request, jsonify, make_response
import bcrypt
from models import get_db
from middleware import signer, get_user_id_from_cookie

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/enter", methods=["POST"])
def enter():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    username = (data.get("username") or "").strip()
    pin = (data.get("pin") or "").strip()

    if not username or len(username) < 1 or len(username) > 30:
        return jsonify({"error": "Username must be 1-30 characters"}), 400
    if not pin or len(pin) != 4 or not pin.isdigit():
        return jsonify({"error": "PIN must be exactly 4 digits"}), 400

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if user:
        # Existing user -- verify PIN
        if not bcrypt.checkpw(pin.encode("utf-8"), user["pin_hash"].encode("utf-8")):
            db.close()
            return jsonify({"error": "Wrong PIN"}), 403

        user_id = user["id"]
        submitted = user["submitted_at"] is not None
    else:
        # New user -- create account
        pin_hash = bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor = db.execute(
            "INSERT INTO users (username, pin_hash) VALUES (?, ?)",
            (username, pin_hash),
        )
        db.commit()
        user_id = cursor.lastrowid
        submitted = False

    # Load existing picks
    picks_rows = db.execute(
        "SELECT category_id, nominee_id FROM picks WHERE user_id = ?", (user_id,)
    ).fetchall()
    picks = {str(r["category_id"]): r["nominee_id"] for r in picks_rows}
    db.close()

    token = signer.dumps({"user_id": user_id})
    resp = make_response(jsonify({
        "user_id": user_id,
        "username": username,
        "submitted": submitted,
        "ballot": picks,
    }))
    resp.set_cookie(
        "ballot_token",
        token,
        httponly=True,
        samesite="Lax",
        max_age=30 * 24 * 3600,
    )
    return resp


@auth_bp.route("/api/auth/check", methods=["POST"])
def check():
    user_id = get_user_id_from_cookie()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        db.close()
        return jsonify({"error": "User not found"}), 401

    picks_rows = db.execute(
        "SELECT category_id, nominee_id FROM picks WHERE user_id = ?", (user_id,)
    ).fetchall()
    picks = {str(r["category_id"]): r["nominee_id"] for r in picks_rows}
    db.close()

    return jsonify({
        "user_id": user["id"],
        "username": user["username"],
        "submitted": user["submitted_at"] is not None,
        "ballot": picks,
    })


@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"ok": True}))
    resp.delete_cookie("ballot_token")
    return resp
