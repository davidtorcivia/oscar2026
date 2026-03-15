import os

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "oscar2026")
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
DB_PATH = os.environ.get("DB_PATH", "/data/oscar.db")
