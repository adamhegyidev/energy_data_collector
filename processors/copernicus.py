from pathlib import Path

import pandas as pd
import xarray as xr


def netcdf_to_dataframe(
    netcdf_file,
    location=None,
):
    ds = xr.open_dataset(
        netcdf_file,
    )

    df = ds.to_dataframe().reset_index()

    df.rename(
        columns={
            "valid_time": "timestamp_utc",
        },
        inplace=True,
    )

    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"],
        utc=True,
    )

    df["timestamp_local"] = (
        df["timestamp_utc"]
        .dt.tz_convert("Europe/Budapest")
    )

    df.insert(
        1,
        "timestamp_local",
        df.pop("timestamp_local"),
    )

    if location:
        df.insert(
            2,
            "location",
            location,
        )
        
    return df


def save_parquet(
    df,
    output_file,
):
    output_file = Path(
        output_file,
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        output_file,
        index=False,
    )

    return output_file