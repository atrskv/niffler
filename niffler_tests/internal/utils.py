import random
from datetime import datetime, timedelta, timezone


def random_recent_days(days=30):
    now = datetime.now(timezone.utc)
    delta = timedelta(days=random.randint(0, days))
    return now - delta
