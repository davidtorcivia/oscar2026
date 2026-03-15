from flask import Blueprint, request, jsonify
from models import get_db
from middleware import get_user_id_from_cookie

ballot_bp = Blueprint("ballot", __name__)


@ballot_bp.route("/api/categories", methods=["GET"])
def get_categories():
    db = get_db()
    cats = db.execute("SELECT * FROM categories ORDER BY sort_order").fetchall()
    result = []
    for cat in cats:
        nominees = db.execute(
            "SELECT id, name, subtitle, is_winner FROM nominees WHERE category_id = ? ORDER BY id",
            (cat["id"],),
        ).fetchall()
        result.append({
            "id": cat["id"],
            "slug": cat["slug"],
            "name": cat["name"],
            "sort_order": cat["sort_order"],
            "nominees": [
                {
                    "id": n["id"],
                    "name": n["name"],
                    "subtitle": n["subtitle"],
                    "is_winner": bool(n["is_winner"]),
                }
                for n in nominees
            ],
        })
    db.close()
    return jsonify({"categories": result})


@ballot_bp.route("/api/ballot/<int:user_id>", methods=["GET"])
def get_ballot(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        db.close()
        return jsonify({"error": "User not found"}), 404

    picks_rows = db.execute(
        "SELECT category_id, nominee_id FROM picks WHERE user_id = ?", (user_id,)
    ).fetchall()
    picks = {str(r["category_id"]): r["nominee_id"] for r in picks_rows}

    # Calculate score
    score = 0
    total = 0
    for cat_id_str, nominee_id in picks.items():
        winner = db.execute(
            "SELECT id FROM nominees WHERE category_id = ? AND is_winner = 1",
            (int(cat_id_str),),
        ).fetchone()
        if winner:
            total += 1
            if winner["id"] == nominee_id:
                score += 1

    db.close()
    return jsonify({
        "picks": picks,
        "score": score,
        "total": total,
        "submitted": user["submitted_at"] is not None,
    })


@ballot_bp.route("/api/ballot/<int:user_id>", methods=["PUT"])
def save_ballot(user_id):
    cookie_uid = get_user_id_from_cookie()
    if cookie_uid != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        db.close()
        return jsonify({"error": "User not found"}), 404
    if user["submitted_at"]:
        db.close()
        return jsonify({"error": "Ballot already submitted"}), 403

    data = request.get_json()
    picks = data.get("picks", {})

    for cat_id_str, nominee_id in picks.items():
        cat_id = int(cat_id_str)
        # Verify nominee belongs to category
        nom = db.execute(
            "SELECT id FROM nominees WHERE id = ? AND category_id = ?",
            (nominee_id, cat_id),
        ).fetchone()
        if not nom:
            db.close()
            return jsonify({"error": f"Invalid nominee {nominee_id} for category {cat_id}"}), 400

        db.execute(
            "INSERT INTO picks (user_id, category_id, nominee_id) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id, category_id) DO UPDATE SET nominee_id = ?, picked_at = CURRENT_TIMESTAMP",
            (user_id, cat_id, nominee_id, nominee_id),
        )

    db.commit()
    db.close()
    return jsonify({"ok": True})


@ballot_bp.route("/api/ballot/<int:user_id>/submit", methods=["POST"])
def submit_ballot(user_id):
    cookie_uid = get_user_id_from_cookie()
    if cookie_uid != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        db.close()
        return jsonify({"error": "User not found"}), 404
    if user["submitted_at"]:
        db.close()
        return jsonify({"error": "Ballot already submitted"}), 403

    # Save any picks sent with the submit request
    data = request.get_json() or {}
    picks = data.get("picks", {})
    for cat_id_str, nominee_id in picks.items():
        cat_id = int(cat_id_str)
        nom = db.execute(
            "SELECT id FROM nominees WHERE id = ? AND category_id = ?",
            (nominee_id, cat_id),
        ).fetchone()
        if not nom:
            db.close()
            return jsonify({"error": f"Invalid nominee {nominee_id} for category {cat_id}"}), 400
        db.execute(
            "INSERT INTO picks (user_id, category_id, nominee_id) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id, category_id) DO UPDATE SET nominee_id = ?, picked_at = CURRENT_TIMESTAMP",
            (user_id, cat_id, nominee_id, nominee_id),
        )

    # Verify all 24 categories have picks
    total_cats = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    user_picks = db.execute(
        "SELECT COUNT(*) FROM picks WHERE user_id = ?", (user_id,)
    ).fetchone()[0]

    if user_picks < total_cats:
        db.commit()
        db.close()
        return jsonify({
            "error": f"All {total_cats} categories must have a pick. You have {user_picks}."
        }), 400

    db.execute(
        "UPDATE users SET submitted_at = CURRENT_TIMESTAMP WHERE id = ?", (user_id,)
    )
    db.commit()
    db.close()
    return jsonify({"ok": True})
