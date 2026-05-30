from pathlib import Path

import warnings

import pandas as pd

warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style.*"
)

def xlsx_to_dataframe(
    xlsx_file,
    dataset,
):
    xlsx_file = Path(xlsx_file)

    df = pd.read_excel(
        xlsx_file,
    )

    if "Időpont" not in df.columns:
        raise ValueError(
            "Missing 'Időpont' column"
        )

    timestamp_utc = pd.to_datetime(
        df["Időpont"],
        utc=True,
    )

    timestamp_local = timestamp_utc.dt.tz_convert(
        "Europe/Budapest"
    )

    df["timestamp_utc"] = timestamp_utc
    df["timestamp_local"] = timestamp_local

    df.drop(
        columns=["Időpont"],
        inplace=True,
    )

    data_columns = [
        column
        for column in df.columns
        if column not in [
            "timestamp_utc",
            "timestamp_local",
        ]
    ]

    df.dropna(
        subset=data_columns,
        how="all",
        inplace=True,
    )

    df.insert(
        0,
        "timestamp_utc",
        df.pop("timestamp_utc"),
    )

    df.insert(
        1,
        "timestamp_local",
        df.pop("timestamp_local"),
    )

    df.insert(
        2,
        "dataset",
        dataset,
    )

    return df

def save_parquet(
    df,
    output_file,
):
    output_file = Path(output_file)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        output_file,
        index=False,
    )

    return output_file