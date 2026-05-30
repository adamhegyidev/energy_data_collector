import shutil
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

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        nc_files = [
            name for name in zip_ref.namelist()
            if name.endswith(".nc")
        ]

        if not nc_files:
            raise FileNotFoundError(
                f"No NetCDF file found in {zip_file}"
            )

        with zip_ref.open(nc_files[0]) as source:
            with open(output_file, "wb") as target:
                shutil.copyfileobj(source, target)

    return output_file