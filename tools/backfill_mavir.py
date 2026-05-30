import time
import argparse
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from collectors.mavir import download_chart
from storage.raw import save_raw_file
from database.logging import init_db, log_download
from utils.config import get_mavir_sources


def to_millis(dt):
    return int(dt.timestamp() * 1000)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Backfill MAVIR historical data"
    )

    parser.add_argument("--from", dest="from_date", required=True)
    parser.add_argument("--to", dest="to_date", required=True)
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--max-days", type=int, default=30)
    parser.add_argument("--sleep", type=int, default=15)

    return parser.parse_args()

def split_range(start_dt, end_dt, max_days=30):
    current = start_dt

    while current < end_dt:
        next_dt = min(current + timedelta(days=max_days), end_dt)
        yield current, next_dt
        current = next_dt


def main():
    init_db()
    
    args = parse_args()

    tz = ZoneInfo("Europe/Budapest")

    start_dt = datetime.fromisoformat(args.from_date).replace(tzinfo=tz)
    end_dt = datetime.fromisoformat(args.to_date).replace(tzinfo=tz)

    sources = get_mavir_sources()

    for dataset, settings in sources.items():
        if args.dataset and dataset != args.dataset:
            continue

        print(f"Backfill dataset: {dataset}")

        for chunk_start, chunk_end in split_range(
            start_dt,
            end_dt,
            max_days=args.max_days,
        ):
            print(f"  {chunk_start.date()} -> {chunk_end.date()}")

            try:
                data = download_chart(
                    chart_id=settings["chart_id"],
                    from_time=to_millis(chunk_start),
                    to_time=to_millis(chunk_end),
                    period=settings["export"]["period"],
                )

                file_path = save_raw_file(
                    source="mavir",
                    dataset=dataset,
                    date_value=chunk_start.date(),
                    content=data,
                    extension=settings["export"]["type"],
                )

                log_download(
                    source="mavir",
                    category=settings.get("category"),
                    dataset=dataset,
                    start_date=chunk_start.date(),
                    end_date=chunk_end.date(),
                    requested_frequency=settings.get("requested_frequency"),
                    actual_frequency=None,
                    file_path=file_path,
                    status="success",
                )

                print(f"  Saved: {file_path}")

            except Exception as error:
                log_download(
                    source="mavir",
                    category=settings.get("category"),
                    dataset=dataset,
                    start_date=chunk_start.date(),
                    end_date=chunk_end.date(),
                    requested_frequency=settings.get("requested_frequency"),
                    actual_frequency=None,
                    status="failed",
                    error_message=str(error),
                )

                print(f"  ERROR: {error}")

            time.sleep(
		random.randint(25,45)
	    )


if __name__ == "__main__":
    main()
