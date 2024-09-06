"""
Module to process a Digital Elevation Model (DEM) raster file.
"""

from spai.storage import Storage
import rasterio
import richdem as rd


def process_dem(storage: Storage) -> None:
    """
    Process the Digital Elevation Model (DEM) raster file.

    Parameters
    ----------
    storage : Storage
        The storage object to read and write files.

    Returns
    -------
    None
    """
    with rasterio.open(storage.get_path("dem.tif")) as dem:
        dem_array = dem.read(1)
        crs = dem.crs
        transform = dem.transform

        dem_rich = rd.rdarray(dem_array, no_data=np.nan)

        aspect = rd.TerrainAttribute(dem_rich, attrib="aspect")
        slope = rd.TerrainAttribute(dem_rich, attrib="slope_riserun")

        # Define the output file paths
        slope_file = storage.get_path("slope.tif")
        aspect_file = storage.get_path("aspect.tif")

        # Write the slope array to a GeoTIFF file
        with rasterio.open(
            slope_file,
            "w",
            driver="GTiff",
            height=slope.shape[0],
            width=slope.shape[1],
            count=1,
            dtype=slope.dtype,
            crs=crs,
            transform=transform,
        ) as dst:
            dst.write(slope, 1)

        # Write the aspect array to a GeoTIFF file
        with rasterio.open(
            aspect_file,
            "w",
            driver="GTiff",
            height=aspect.shape[0],
            width=aspect.shape[1],
            count=1,
            dtype=aspect.dtype,
            crs=crs,
            transform=transform,
        ) as dst:
            dst.write(aspect, 1)
