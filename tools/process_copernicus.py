from pathlib import Path

from processors.copernicus import (
    netcdf_to_dataframe,
    save_parquet,
)


def main():
    dataset = "era5_hungary_points"
    location_name = "budapest"
    year = 2024
    month = 1

    nc_file = (
        Path("data")
        / "raw"
        / "copernicus"
        / dataset
        / location_name
        / str(year)
        / f"{year}-{month:02d}.nc"
    )

    df = netcdf_to_dataframe(
        nc_file,
        location=location_name,
    )

    print(df.head())
    print(df.shape)

    output_file = (
        Path("data")
        / "processed"
        / "copernicus"
        / dataset
        / location_name
        / str(year)
        / f"{year}-{month:02d}.parquet"
    )

    save_parquet(
        df,
        output_file,
    )

    print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()