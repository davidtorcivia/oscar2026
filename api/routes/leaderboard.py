from flask import Blueprint, jsonify
from models import get_db

leaderboard_bp = Blueprint("leaderboard", __name__)


@leaderboard_bp.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    db = get_db()

    # Get all winners
    winners = {}
    winner_rows = db.execute(
        "SELECT category_id, id FROM nominees WHERE is_winner = 1"
    ).fetchall()
    for w in winner_rows:
        winners[w["category_id"]] = w["id"]

    total_announced = len(winners)

    # Get all submitted users and their picks
    users = db.execute(
        "SELECT id, username, submitted_at FROM users WHERE submitted_at IS NOT NULL ORDER BY submitted_at"
    ).fetchall()

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
            "user_id": user["id"],
            "username": user["username"],
            "score": score,
            "total": total_announced,
            "submitted_at": user["submitted_at"],
        })

    # Sort by score desc, then by submitted_at asc (earlier is better for tiebreaker display)
    result.sort(key=lambda x: (-x["score"], x["submitted_at"] or ""))

    # Assign ranks with ties -- same score = same rank
    for i, entry in enumerate(result):
        if i == 0 or entry["score"] != result[i - 1]["score"]:
            entry["rank"] = i + 1
        else:
            entry["rank"] = result[i - 1]["rank"]

    db.close()
    return jsonify({"users": result, "total_announced": total_announced})


@leaderboard_bp.route("/api/results", methods=["GET"])
def get_results():
    db = get_db()
    cats = db.execute("SELECT * FROM categories ORDER BY sort_order").fetchall()
    result = []
    for cat in cats:
        winner = db.execute(
            "SELECT id, name, subtitle FROM nominees WHERE category_id = ? AND is_winner = 1",
            (cat["id"],),
        ).fetchone()
        result.append({
            "id": cat["id"],
            "slug": cat["slug"],
            "name": cat["name"],
            "winner": {
                "id": winner["id"],
                "name": winner["name"],
                "subtitle": winner["subtitle"],
            } if winner else None,
        })
    db.close()
    return jsonify({"categories": result})
