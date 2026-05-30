from pathlib import Path

import pandas as pd


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

    timestamp = pd.to_datetime(
        df["Időpont"]
    )

    df["timestamp_utc"] = (
        timestamp.dt.tz_convert("UTC")
    )

    df.drop(
        columns=["Időpont"],
        inplace=True,
    )

    df.insert(
        0,
        "timestamp_utc",
        df.pop("timestamp_utc"),
    )

    df.insert(
        1,
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