from pathlib import Path

from processors.mavir import (
    xlsx_to_dataframe,
    save_parquet,
)


def main():
    dataset = "frekvencia"
    year = 2024
    month = 1

    xlsx_file = (
        Path("data")
        / "raw"
        / "mavir"
        / dataset
        / str(year)
        / f"{year}-{month:02d}.xlsx"
    )

    df = xlsx_to_dataframe(
        xlsx_file,
        dataset=dataset,
    )

    print(df.head())
    print(df.shape)

    output_file = (
        Path("data")
        / "processed"
        / "mavir"
        / dataset
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
