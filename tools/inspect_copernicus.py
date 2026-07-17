from pathlib import Path
import xarray as xr

nc_file = Path(
    "data/raw/copernicus/era5_hungary_points/budapest/2004/2004-01.nc"
)

ds = xr.open_dataset(nc_file)

print(ds)
print()
print("Variables:")
print(list(ds.data_vars))