from pathlib import Path
import xarray as xr

nc_file = next(
    Path(
        "data/raw/copernicus/era5_hungary_points/budapest/2024/01/extracted"
    ).glob("*.nc")
)

ds = xr.open_dataset(nc_file)

print(ds)