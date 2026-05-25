from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def previous_full_day(timezone="Europe/Budapest"):
    tz = ZoneInfo(timezone)

    today = datetime.now(tz).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    yesterday = today - timedelta(days=1)

    return yesterday, today