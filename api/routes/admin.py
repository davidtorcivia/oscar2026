from flask import Blueprint, request, jsonify, session
from models import get_db
from config import ADMIN_PASSWORD
from middleware import require_admin

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    password = data.get("password", "")
    if password == ADMIN_PASSWORD:
        session["is_admin"] = True
        return jsonify({"ok": True})
    return jsonify({"error": "Wrong password"}), 403


@admin_bp.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("is_admin", None)
    return jsonify({"ok": True})


@admin_bp.route("/api/admin/check", methods=["GET"])
@require_admin
def admin_check():
    return jsonify({"ok": True})


@admin_bp.route("/api/admin/users", methods=["GET"])
@require_admin
def get_users():
    db = get_db()
    users = db.execute(
        "SELECT id, username, created_at, submitted_at FROM users ORDER BY username"
    ).fetchall()

    # Get winners for scoring
    winners = {}
    winner_rows = db.execute(
        "SELECT category_id, id FROM nominees WHERE is_winner = 1"
    ).fetchall()
    for w in winner_rows:
        winners[w["category_id"]] = w["id"]

    result = []
    for user in users:
        picks = db.execute(
            "SELECT category_id, nominee_id FROM picks WHERE user_id = ?",
            (user["id"],),
        ).fetchall()

        score = 0
        for pick in picks:
            if winners.get(pick["category_id"]) == pick["nominee_id"]:
                score += 1

        result.append({
            "id": user["id"],
            "username": user["username"],
            "created_at": user["created_at"],
            "submitted_at": user["submitted_at"],
            "picks_count": len(picks),
            "score": score,
        })

    db.close()
    return jsonify({"users": result})


@admin_bp.route("/api/admin/stats", methods=["GET"])
@require_admin
def get_stats():
    db = get_db()
    total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    submitted = db.execute(
        "SELECT COUNT(*) FROM users WHERE submitted_at IS NOT NULL"
    ).fetchone()[0]
    drafting = total_users - submitted

    # Most picked per category
    cats = db.execute("SELECT * FROM categories ORDER BY sort_order").fetchall()
    category_stats = []
    for cat in cats:
        top = db.execute(
            """SELECT n.name, n.subtitle, COUNT(p.id) as count
               FROM nominees n
               LEFT JOIN picks p ON p.nominee_id = n.id
               WHERE n.category_id = ?
               GROUP BY n.id
               ORDER BY count DESC
               LIMIT 1""",
            (cat["id"],),
        ).fetchone()
        category_stats.append({
            "category": cat["name"],
            "top_pick": top["name"] if top else None,
            "top_pick_subtitle": top["subtitle"] if top else None,
            "top_count": top["count"] if top else 0,
        })

    db.close()
    return jsonify({
        "total_users": total_users,
        "submitted": submitted,
        "drafting": drafting,
        "category_stats": category_stats,
    })


@admin_bp.route("/api/admin/winner", methods=["POST"])
@require_admin
def set_winner():
    data = request.get_json()
    category_id = data.get("category_id")
    nominee_id = data.get("nominee_id")

    if not category_id or not nominee_id:
        return jsonify({"error": "category_id and nominee_id required"}), 400

    db = get_db()
    # Clear existing winner for this category
    db.execute(
        "UPDATE nominees SET is_winner = 0 WHERE category_id = ?", (category_id,)
    )
    # Set new winner
    db.execute(
        "UPDATE nominees SET is_winner = 1 WHERE id = ? AND category_id = ?",
        (nominee_id, category_id),
    )
    db.commit()
    db.close()
    return jsonify({"ok": True})


@admin_bp.route("/api/admin/winner", methods=["DELETE"])
@require_admin
def clear_winner():
    data = request.get_json()
    category_id = data.get("category_id")
    if not category_id:
        return jsonify({"error": "category_id required"}), 400

    db = get_db()
    db.execute(
        "UPDATE nominees SET is_winner = 0 WHERE category_id = ?", (category_id,)
    )
    db.commit()
    db.close()
    return jsonify({"ok": True})


@admin_bp.route("/api/admin/user/<int:user_id>", methods=["DELETE"])
@require_admin
def delete_user(user_id):
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        db.close()
        return jsonify({"error": "User not found"}), 404

    db.execute("DELETE FROM picks WHERE user_id = ?", (user_id,))
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    db.close()
    return jsonify({"ok": True})


@admin_bp.route("/api/admin/category/<int:cat_id>", methods=["PUT"])
@require_admin
def update_category(cat_id):
    data = request.get_json()
    db = get_db()

    cat = db.execute("SELECT * FROM categories WHERE id = ?", (cat_id,)).fetchone()
    if not cat:
        db.close()
        return jsonify({"error": "Category not found"}), 404

    name = data.get("name", cat["name"])
    nominees_data = data.get("nominees")
    force = data.get("force", False)
    warnings = []

    if nominees_data is not None:
        existing = db.execute(
            "SELECT id, name FROM nominees WHERE category_id = ?", (cat_id,)
        ).fetchall()
        existing_names = {n["name"] for n in existing}
        new_names = {n["name"] for n in nominees_data}
        removed = existing_names - new_names

        if removed:
            for rname in removed:
                nom = db.execute(
                    "SELECT id FROM nominees WHERE category_id = ? AND name = ?",
                    (cat_id, rname),
                ).fetchone()
                if nom:
                    # Check if it's a winner
                    is_w = db.execute(
                        "SELECT is_winner FROM nominees WHERE id = ?", (nom["id"],)
                    ).fetchone()
                    if is_w and is_w["is_winner"]:
                        db.close()
                        return jsonify({
                            "error": f"Cannot remove winner '{rname}'. Clear winner first."
                        }), 400

                    affected = db.execute(
                        "SELECT u.username FROM picks p JOIN users u ON u.id = p.user_id WHERE p.nominee_id = ?",
                        (nom["id"],),
                    ).fetchall()
                    if affected:
                        warnings.append({
                            "nominee": rname,
                            "affected_users": [a["username"] for a in affected],
                        })

            if warnings and not force:
                db.close()
                return jsonify({"warnings": warnings, "requires_force": True}), 409

            # Proceed with removal
            for rname in removed:
                nom = db.execute(
                    "SELECT id FROM nominees WHERE category_id = ? AND name = ?",
                    (cat_id, rname),
                ).fetchone()
                if nom:
                    db.execute("DELETE FROM picks WHERE nominee_id = ?", (nom["id"],))
                    db.execute("DELETE FROM nominees WHERE id = ?", (nom["id"],))

        # Add new nominees
        for n in nominees_data:
            if n["name"] not in existing_names:
                db.execute(
                    "INSERT INTO nominees (category_id, name, subtitle) VALUES (?, ?, ?)",
                    (cat_id, n["name"], n.get("subtitle")),
                )

    db.execute("UPDATE categories SET name = ? WHERE id = ?", (name, cat_id))
    db.commit()
    db.close()
    return jsonify({"ok": True, "warnings": warnings})


@admin_bp.route("/api/admin/category", methods=["POST"])
@require_admin
def add_category():
    data = request.get_json()
    name = data.get("name")
    nominees_data = data.get("nominees", [])

    if not name:
        return jsonify({"error": "Name required"}), 400

    slug = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
    db = get_db()
    max_order = db.execute("SELECT MAX(sort_order) FROM categories").fetchone()[0] or 0
    cursor = db.execute(
        "INSERT INTO categories (slug, name, sort_order, num_nominees) VALUES (?, ?, ?, ?)",
        (slug, name, max_order + 1, len(nominees_data) or 5),
    )
    cat_id = cursor.lastrowid

    for n in nominees_data:
        db.execute(
            "INSERT INTO nominees (category_id, name, subtitle) VALUES (?, ?, ?)",
            (cat_id, n["name"], n.get("subtitle")),
        )

    db.commit()
    db.close()
    return jsonify({"ok": True, "id": cat_id})


@admin_bp.route("/api/admin/category/<int:cat_id>", methods=["DELETE"])
@require_admin
def delete_category(cat_id):
    db = get_db()
    picks_count = db.execute(
        "SELECT COUNT(*) FROM picks WHERE category_id = ?", (cat_id,)
    ).fetchone()[0]

    if picks_count > 0:
        force = request.args.get("force") == "true"
        if not force:
            db.close()
            return jsonify({
                "error": f"{picks_count} picks exist for this category. Use ?force=true to delete.",
                "picks_count": picks_count,
            }), 409

    db.execute("DELETE FROM picks WHERE category_id = ?", (cat_id,))
    db.execute("DELETE FROM nominees WHERE category_id = ?", (cat_id,))
    db.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
    db.commit()
    db.close()
    return jsonify({"ok": True})
