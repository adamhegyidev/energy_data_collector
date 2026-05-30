import cdsapi

client = cdsapi.Client()

client.retrieve(
    "reanalysis-era5-single-levels",
    {
        "product_type": "reanalysis",
        "variable": [
            "2m_temperature",
        ],
        "year": "2024",
        "month": "01",
        "day": "01",
        "time": [
            "00:00",
            "12:00",
        ],
        "data_format": "netcdf",
        "download_format": "unarchived",
    },
    "test_era5.nc",
)

print("Download completed")