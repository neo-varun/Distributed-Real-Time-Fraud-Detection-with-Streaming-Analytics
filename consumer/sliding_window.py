from collections import defaultdict
from datetime import datetime

user_activity = defaultdict(list)

WINDOW_SIZE = 60


def update_window(user, timestamp):

    now = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    user_activity[user].append(now)

    user_activity[user] = [
        t for t in user_activity[user] if (now - t).seconds <= WINDOW_SIZE
    ]

    return len(user_activity[user])
