from datetime import datetime
from zoneinfo import ZoneInfo


USER_TZ = ZoneInfo("America/Edmonton")
TSX_TZ = ZoneInfo("America/Toronto")


def get_chat_time_context() -> str:
    user_now = datetime.now(USER_TZ)
    tsx_now = datetime.now(TSX_TZ)

    weekday = tsx_now.weekday()
    open_time = tsx_now.replace(hour=9, minute=30, second=0, microsecond=0)
    close_time = tsx_now.replace(hour=16, minute=0, second=0, microsecond=0)

    tsx_regular_open = weekday < 5 and open_time <= tsx_now <= close_time

    return (
        f"User local time: {user_now.strftime('%Y-%m-%d %I:%M %p %Z')}\n"
        f"TSX exchange time: {tsx_now.strftime('%Y-%m-%d %I:%M %p %Z')}\n"
        f"TSX regular session open right now: {tsx_regular_open}\n"
        "TSX regular hours: Monday-Friday, 9:30 AM-4:00 PM America/Toronto.\n"
        "Do not guess current market hours. Use this time context."
    )
