from pathlib import Path

from collectors.copernicus import download_era5_point
from utils.config import get_copernicus_sources


def main():
    sources = get_copernicus_sources()

    source = sources["era5_hungary_points"]

    location_name = "budapest"
    location = source["locations"][location_name]

    output_file = (
        Path("data")
        / "raw"
        / "copernicus"
        / "era5_hungary_points"
        / location_name
        / "2024"
        / "01"
        / "2024-01.nc"
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    download_era5_point(
        dataset=source["dataset"],
        variables=source["variables"],
        latitude=location["latitude"],
        longitude=location["longitude"],
        start_date="2024-01-01",
        end_date="2024-01-31",
        output_file=output_file,
        data_format=source["format"]["data_format"],
    )

    print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()