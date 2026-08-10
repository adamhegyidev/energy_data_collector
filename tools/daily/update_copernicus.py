import argparse
from datetime import date
from pathlib import Path

from collectors.copernicus import download_era5_point
from processors.copernicus import (
    netcdf_to_dataframe,
    save_parquet,
)
from utils.config import get_copernicus_sources


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Update current Copernicus ERA5 "
            "monthly time-series data."
        ),
        formatter_class=(
            argparse.ArgumentDefaultsHelpFormatter
        ),
    )

    parser.add_argument(
        "--location",
        default=None,
        help=(
            "Location name from config "
            "(default: all locations)"
        ),
    )

    return parser.parse_args()


def current_month_range():
    today = date.today()

    start_date = date(
        today.year,
        today.month,
        1,
    )

    return (
        today.year,
        today.month,
        start_date.isoformat(),
        today.isoformat(),
    )


def update_copernicus(
    location_filter=None,
):
    sources = get_copernicus_sources()

    source_name = (
        "era5_hungary_points"
    )

    source = sources[
        source_name
    ]

    if not source.get(
        "enabled",
        False,
    ):
        print(
            f"Copernicus source disabled: "
            f"{source_name}"
        )
        return True

    locations = source[
        "locations"
    ]

    if (
        location_filter
        and location_filter
        not in locations
    ):
        raise ValueError(
            f"Unknown location: "
            f"{location_filter}"
        )

    (
        year,
        month,
        start_date,
        end_date,
    ) = current_month_range()

    print(
        "Copernicus current month update: "
        f"{start_date} -> {end_date}"
    )

    selected_locations = [
        (
            location_name,
            location,
        )
        for location_name, location
        in locations.items()
        if (
            location_filter is None
            or location_name
            == location_filter
        )
    ]

    total_locations = len(
        selected_locations
    )

    success_count = 0
    error_count = 0

    for index, (
        location_name,
        location,
    ) in enumerate(
        selected_locations,
        start=1,
    ):
        print()
        print(
            f"[{index}/{total_locations}] "
            f"Updating Copernicus: "
            f"{location_name}"
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

        parquet_file = (
            Path("data")
            / "processed"
            / "copernicus"
            / source_name
            / location_name
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

            nc_file = download_era5_point(
                dataset=source[
                    "dataset"
                ],
                variables=source[
                    "variables"
                ],
                latitude=location[
                    "latitude"
                ],
                longitude=location[
                    "longitude"
                ],
                start_date=start_date,
                end_date=end_date,
                output_file=raw_file,
                data_format=source[
                    "format"
                ][
                    "data_format"
                ],
            )

            print(
                f"  RAW: {nc_file}"
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
                f"  PARQUET: "
                f"{parquet_file}"
            )

            print(
                f"  Rows: {len(df):,}"
            )

            if (
                not df.empty
                and "timestamp_local"
                in df.columns
            ):
                print(
                    f"  First: "
                    f"{df['timestamp_local'].min()}"
                )

                print(
                    f"  Last:  "
                    f"{df['timestamp_local'].max()}"
                )

            success_count += 1

        except Exception as exc:
            error_count += 1

            print(
                f"  ERROR "
                f"{location_name}: "
                f"{exc}"
            )

    print()

    print(
        "Copernicus update finished."
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

    update_copernicus(
        location_filter=(
            args.location
        ),
    )


if __name__ == "__main__":
    main()