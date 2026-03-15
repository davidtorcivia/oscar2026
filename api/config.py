import os
from datetime import datetime, timezone, timedelta

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "oscar2026")
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
DB_PATH = os.environ.get("DB_PATH", "/data/oscar.db")

# Ballots auto-lock at 7:30 PM EDT (UTC-4) on March 15, 2026
# This is after Conan's monologue but before the first award
EDT = timezone(timedelta(hours=-4))
LOCK_TIME = datetime(2026, 3, 15, 19, 30, 0, tzinfo=EDT)


def is_locked():
    return datetime.now(timezone.utc) >= LOCK_TIME
