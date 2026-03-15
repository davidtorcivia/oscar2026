from flask import Flask
from config import SECRET_KEY
from models import init_db
from seed import seed_db
from routes.auth import auth_bp
from routes.ballot import ballot_bp
from routes.leaderboard import leaderboard_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    app.register_blueprint(auth_bp)
    app.register_blueprint(ballot_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        init_db()
        if seed_db():
            print("Database seeded with 24 categories and nominees.")
        else:
            print("Database already contains data, skipping seed.")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
