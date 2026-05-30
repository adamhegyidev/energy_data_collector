import zipfile
from pathlib import Path

import cdsapi


def download_era5_point(
    dataset,
    variables,
    latitude,
    longitude,
    start_date,
    end_date,
    output_file,
    data_format="netcdf",
):
    output_file = Path(output_file)

    zip_file = output_file.with_suffix(".zip")
    extract_dir = output_file.parent / "extracted"

    client = cdsapi.Client()

    request = {
        "variable": variables,
        "date": [
            f"{start_date}/{end_date}"
        ],
        "location": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "data_format": data_format,
    }

    zip_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    client.retrieve(
        dataset,
        request,
        str(zip_file),
    )

    extract_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    extracted_files = list(
        extract_dir.glob("*.nc")
    )

    if not extracted_files:
        raise FileNotFoundError(
            f"No NetCDF file found in {extract_dir}"
        )

    return extracted_files[0]