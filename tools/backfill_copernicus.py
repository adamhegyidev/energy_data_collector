import argparse
from datetime import date, timedelta
from pathlib import Path

from collectors.copernicus import download_era5_point
from processors.copernicus import (
    netcdf_to_dataframe,
    save_parquet,
)
from utils.config import get_copernicus_sources


def parse_args():
    parser = argparse.ArgumentParser(
        description="Backfill Copernicus ERA5 time-series data.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        "--location",
        default=None,
        help="Location name from config (default: all locations)",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing raw and processed files",
    )

    return parser.parse_args()


def iter_months(from_month, to_month):
    start_year, start_month = map(
        int,
        from_month.split("-"),
    )

    end_year, end_month = map(
        int,
        to_month.split("-"),
    )

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


def month_date_range(year, month):
    start_date = date(year, month, 1)

    next_year, next_month_value = next_month(year, month)

    next_month_start = date(
        next_year,
        next_month_value,
        1,
    )

    end_date = next_month_start - timedelta(days=1)

    return (
        start_date.isoformat(),
        end_date.isoformat(),
    )


def main():
    args = parse_args()

    sources = get_copernicus_sources()

    source_name = "era5_hungary_points"
    source = sources[source_name]

    locations = source["locations"]

    if (
        args.location
        and args.location not in locations
    ):
        raise ValueError(
            f"Unknown location: {args.location}"
        )

    for location_name, location in locations.items():

        if (
            args.location
            and location_name != args.location
        ):
            continue

        for year, month in iter_months(
            args.from_month,
            args.to_month,
        ):

            parquet_file = (
                Path("data")
                / "processed"
                / "copernicus"
                / source_name
                / location_name
                / str(year)
                / f"{year}-{month:02d}.parquet"
            )
            if parquet_file.exists() and not args.overwrite:
                print(
                    f"Skipping existing: {parquet_file}"
                )
                continue

            try:
                print(
                    f"Backfill "
                    f"{location_name} "
                    f"{year}-{month:02d}"
                )

                start_date, end_date = (
                    month_date_range(
                        year,
                        month,
                    )
                )

                raw_file = (
                    Path("data")
                    / "raw"
                    / "copernicus"
                    / source_name
                    / location_name
                    / str(year)
                    / f"{year}-{month:02d}.nc"
                )

                nc_file = download_era5_point(
                    dataset=source["dataset"],
                    variables=source["variables"],
                    latitude=location["latitude"],
                    longitude=location["longitude"],
                    start_date=start_date,
                    end_date=end_date,
                    output_file=raw_file,
                    data_format=source["format"][
                        "data_format"
                    ],
                )

                df = netcdf_to_dataframe(
                    nc_file,
                    location=location_name,
                )

                save_parquet(
                    df,
                    parquet_file,
                )

                print(
                    f"Saved: {parquet_file}"
                )

            except Exception as exc:
                print(
                    f"ERROR "
                    f"{location_name} "
                    f"{year}-{month:02d}: "
                    f"{exc}"
                )


if __name__ == "__main__":
    main()