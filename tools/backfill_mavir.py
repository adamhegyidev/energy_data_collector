import argparse
import random
import time
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from collectors.mavir import download_chart
from database.logging import init_db, log_download
from utils.config import get_mavir_sources


def to_millis(dt):
    return int(dt.timestamp() * 1000)


def parse_args():
    sources = get_mavir_sources()
    dataset_names = "\n  ".join(
        sorted(
            name
            for name, settings in sources.items()
            if settings.get("enabled", False)
        )
    )

    parser = argparse.ArgumentParser(
        description="Backfill MAVIR historical data by full calendar months.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
            Examples:

            One month, one dataset:
                python -m tools.backfill_mavir --from 2024-01 --to 2024-01 --dataset rendszerterheles

            One year, one dataset:
                python -m tools.backfill_mavir --from 2024-01 --to 2024-12 --dataset rendszerterheles

            One year, all enabled datasets:
                python -m tools.backfill_mavir --from 2024-01 --to 2024-12

            Available datasets:

            {dataset_names}
            """,
    )

    parser.add_argument(
        "--from",
        dest="from_month",
        required=True,
        help="Start month (YYYY-MM)",
    )

    parser.add_argument(
        "--to",
        dest="to_month",
        required=True,
        help="End month (YYYY-MM)",
    )

    parser.add_argument(
        "--dataset",
        default=None,
        help="Dataset name from sources.yaml (default: all enabled datasets)",
    )

    parser.add_argument(
        "--sleep-min",
        type=int,
        default=25,
        help="Minimum seconds to wait between requests",
    )

    parser.add_argument(
        "--sleep-max",
        type=int,
        default=45,
        help="Maximum seconds to wait between requests",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing monthly raw files",
    )

    return parser.parse_args()


def iter_months(from_month, to_month):
    start_year, start_month = map(int, from_month.split("-"))
    end_year, end_month = map(int, to_month.split("-"))

    year = start_year
    month = start_month

    while (year, month) <= (end_year, end_month):
        yield year, month

        month += 1

        if month == 13:
            month = 1
            year += 1


def next_month(year, month):
    if month == 12:
        return year + 1, 1

    return year, month + 1


def month_date_range(year, month, timezone="Europe/Budapest"):
    tz = ZoneInfo(timezone)

    start = datetime(
        year,
        month,
        1,
        tzinfo=tz,
    )

    next_year, next_month_value = next_month(
        year,
        month,
    )

    end = datetime(
        next_year,
        next_month_value,
        1,
        tzinfo=tz,
    )

    return start, end


def save_monthly_raw_file(
    source,
    dataset,
    year,
    month,
    content,
    extension,
):
    file_path = (
        Path("data")
        / "raw"
        / source
        / dataset
        / str(year)
        / f"{year}-{month:02d}.{extension}"
    )

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(file_path, "wb") as file:
        file.write(content)

    return file_path


def main():
    init_db()

    args = parse_args()

    sources = get_mavir_sources()

    if args.dataset and args.dataset not in sources:
        raise ValueError(
            f"Unknown dataset: {args.dataset}"
        )

    if args.sleep_min > args.sleep_max:
        raise ValueError(
            "--sleep-min cannot be greater than --sleep-max"
        )

    for dataset, settings in sources.items():
        if args.dataset and dataset != args.dataset:
            continue

        if not settings.get("enabled", False):
            print(f"Skipping disabled dataset: {dataset}")
            continue

        print(f"Backfill dataset: {dataset}")

        for year, month in iter_months(
            args.from_month,
            args.to_month,
        ):
            from_dt, to_dt = month_date_range(
                year,
                month,
            )

            extension = settings["export"]["type"]

            file_path = (
                Path("data")
                / "raw"
                / "mavir"
                / dataset
                / str(year)
                / f"{year}-{month:02d}.{extension}"
            )

            if file_path.exists() and not args.overwrite:
                print(
                    f"  Skipping existing: {file_path}"
                )
                continue

            print(
                f"  {from_dt.date()} -> {to_dt.date()}"
            )

            try:
                data = download_chart(
                    chart_id=settings["chart_id"],
                    from_time=to_millis(from_dt),
                    to_time=to_millis(to_dt),
                    period=settings["export"]["period"],
                )

                file_path = save_monthly_raw_file(
                    source="mavir",
                    dataset=dataset,
                    year=year,
                    month=month,
                    content=data,
                    extension=extension,
                )

                log_download(
                    source="mavir",
                    category=settings.get("category"),
                    dataset=dataset,
                    start_date=from_dt.date(),
                    end_date=to_dt.date(),
                    requested_frequency=settings.get(
                        "requested_frequency"
                    ),
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
                    start_date=from_dt.date(),
                    end_date=to_dt.date(),
                    requested_frequency=settings.get(
                        "requested_frequency"
                    ),
                    actual_frequency=None,
                    status="failed",
                    error_message=str(error),
                )

                print(f"  ERROR: {error}")

            wait_time = random.randint(
                args.sleep_min,
                args.sleep_max,
            )

            print(f"  Waiting {wait_time} seconds...")
            time.sleep(wait_time)


if __name__ == "__main__":
    main()