import argparse
import random
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from collectors.mavir import download_chart
from database.logging import init_db, log_download
from processors.mavir import (
    save_parquet,
    xlsx_to_dataframe,
)
from utils.config import get_mavir_sources


LOCAL_TIMEZONE = "Europe/Budapest"


def to_millis(dt):
    return int(
        dt.timestamp() * 1000
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Update current MAVIR month "
            "for all enabled datasets."
        ),
        formatter_class=(
            argparse.ArgumentDefaultsHelpFormatter
        ),
    )

    parser.add_argument(
        "--dataset",
        default=None,
        help=(
            "Only update one dataset "
            "(default: all enabled datasets)"
        ),
    )

    parser.add_argument(
        "--sleep-min",
        type=int,
        default=5,
        help=(
            "Minimum seconds to wait "
            "between MAVIR requests"
        ),
    )

    parser.add_argument(
        "--sleep-max",
        type=int,
        default=15,
        help=(
            "Maximum seconds to wait "
            "between MAVIR requests"
        ),
    )

    return parser.parse_args()


def current_month_range(
    timezone=LOCAL_TIMEZONE,
):
    tz = ZoneInfo(
        timezone
    )

    now = datetime.now(
        tz
    )

    start = datetime(
        now.year,
        now.month,
        1,
        tzinfo=tz,
    )

    return (
        now.year,
        now.month,
        start,
        now,
    )


def update_mavir(
    dataset_filter=None,
    sleep_min=5,
    sleep_max=15,
):
    init_db()

    if sleep_min > sleep_max:
        raise ValueError(
            "sleep_min cannot be greater "
            "than sleep_max"
        )

    sources = get_mavir_sources()

    if (
        dataset_filter
        and dataset_filter not in sources
    ):
        raise ValueError(
            f"Unknown dataset: "
            f"{dataset_filter}"
        )

    (
        year,
        month,
        from_dt,
        to_dt,
    ) = current_month_range()

    print(
        f"MAVIR current month update: "
        f"{from_dt.isoformat()} -> "
        f"{to_dt.isoformat()}"
    )

    success_count = 0
    error_count = 0

    enabled_datasets = [
        (
            dataset,
            settings,
        )
        for dataset, settings
        in sources.items()
        if settings.get(
            "enabled",
            False,
        )
        and (
            dataset_filter is None
            or dataset == dataset_filter
        )
    ]

    total_datasets = len(
        enabled_datasets
    )

    for index, (
        dataset,
        settings,
    ) in enumerate(
        enabled_datasets,
        start=1,
    ):
        print()
        print(
            f"[{index}/{total_datasets}] "
            f"Updating MAVIR: {dataset}"
        )

        extension = (
            settings["export"]["type"]
        )

        raw_file = (
            Path("data")
            / "raw"
            / "mavir"
            / dataset
            / str(year)
            / f"{year}-{month:02d}.{extension}"
        )

        parquet_file = (
            Path("data")
            / "processed"
            / "mavir"
            / dataset
            / str(year)
            / f"{year}-{month:02d}.parquet"
        )

        try:
            raw_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            parquet_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            data = download_chart(
                chart_id=settings[
                    "chart_id"
                ],
                from_time=to_millis(
                    from_dt
                ),
                to_time=to_millis(
                    to_dt
                ),
                period=settings[
                    "export"
                ][
                    "period"
                ],
            )

            raw_file.write_bytes(
                data
            )

            print(
                f"  RAW: {raw_file}"
            )

            log_download(
                source="mavir",
                category=settings.get(
                    "category"
                ),
                dataset=dataset,
                start_date=(
                    from_dt.date()
                ),
                end_date=(
                    to_dt.date()
                ),
                requested_frequency=(
                    settings.get(
                        "requested_frequency"
                    )
                ),
                actual_frequency=None,
                file_path=raw_file,
                status="success",
            )

            df = xlsx_to_dataframe(
                raw_file,
                dataset=dataset,
            )

            save_parquet(
                df,
                parquet_file,
            )

            print(
                f"  PARQUET: "
                f"{parquet_file}"
            )

            print(
                f"  Rows: {len(df):,}"
            )

            success_count += 1

        except Exception as error:
            error_count += 1

            log_download(
                source="mavir",
                category=settings.get(
                    "category"
                ),
                dataset=dataset,
                start_date=(
                    from_dt.date()
                ),
                end_date=(
                    to_dt.date()
                ),
                requested_frequency=(
                    settings.get(
                        "requested_frequency"
                    )
                ),
                actual_frequency=None,
                status="failed",
                error_message=str(
                    error
                ),
            )

            print(
                f"  ERROR {dataset}: "
                f"{error}"
            )

        # Az utolsó kérés után már
        # felesleges várni.
        if index < total_datasets:
            wait_time = random.randint(
                sleep_min,
                sleep_max,
            )

            print(
                f"  Waiting "
                f"{wait_time} seconds..."
            )

            time.sleep(
                wait_time
            )

    print()
    print(
        "MAVIR update finished."
    )

    print(
        f"  Success: "
        f"{success_count}"
    )

    print(
        f"  Errors: "
        f"{error_count}"
    )

    return error_count == 0


def main():
    args = parse_args()

    update_mavir(
        dataset_filter=args.dataset,
        sleep_min=args.sleep_min,
        sleep_max=args.sleep_max,
    )


if __name__ == "__main__":
    main()