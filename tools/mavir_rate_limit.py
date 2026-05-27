import time
from datetime import datetime
from zoneinfo import ZoneInfo

from collectors.mavir import download_chart


def to_millis(dt):
    return int(dt.timestamp() * 1000)


def main():
    tz = ZoneInfo("Europe/Budapest")

    from_dt = datetime(2026, 5, 24, tzinfo=tz)
    to_dt = datetime(2026, 5, 25, tzinfo=tz)

    chart_id = 4423

    wait_times = [5, 10, 15, 20, 30, 45, 60]

    for wait_time in wait_times:
        print("=" * 80)
        print(f"Testing wait time: {wait_time} seconds")

        try:
            data = download_chart(
                chart_id=chart_id,
                from_time=to_millis(from_dt),
                to_time=to_millis(to_dt),
            )

            print(f"SUCCESS | Size: {len(data)} bytes")

        except Exception as error:
            print(f"FAILED | {error}")

        print(f"Waiting {wait_time} seconds...")
        time.sleep(wait_time)


if __name__ == "__main__":
    main()