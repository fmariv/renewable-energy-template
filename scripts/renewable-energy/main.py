from spai.data.satellite import download_satellite_imagery
from spai.data.hidrology import download_waterways
from spai.data.utilities import (
    download_roads,
    download_buildings,
    download_power_networks,
    download_pipelines,
)
import numpy as np
from spai.storage import Storage
from spai.config import SPAIVars
import geopandas as gpd
import rasterio
import richdem as rd

storage = Storage()["data"]
vars = SPAIVars()


def create_buffer(gdf, buffer_size):
    if not gdf.crs:
        gdf = gdf.set_crs("EPSG:4326")
    gdf_3857 = gdf.to_crs("EPSG:3857")
    # Create a new geodataframe with the buffer
    gdf_3857["geometry"] = gdf_3857.geometry.buffer(buffer_size)
    gdf = gdf_3857.to_crs("EPSG:4326")
    return gdf


def download_wdpa(storage, gdf):
    wdpa = storage.read("wdpa_polygons_ESP.parquet")
    # Filter the wdpa polygons that intersect with the gdf
    wdpa = wdpa[wdpa.intersects(gdf.unary_union)]
    if wdpa.empty:
        print("No wdpa polygons intersect with the gdf")
        return
    storage.create(wdpa, "protected.geojson")


if __name__ == "__main__":
    aoi = vars["AOI"]
    gdf = gpd.GeoDataFrame.from_features(aoi)
    # Download DEM
    dem = download_satellite_imagery(
        storage, gdf, collection="cop-dem-glo-30", name="dem.tif"
    )
    # Download Land Cover
    lc = download_satellite_imagery(
        storage, gdf, date="2021", collection="esa-worldcover", name="land_cover.tif"
    )
    # Download geophysical and utilities data
    # Buffer 5 km
    gdf_buffer = create_buffer(gdf, 5000)
    download_waterways(storage, gdf_buffer)
    download_roads(storage, gdf_buffer)
    download_buildings(storage, gdf_buffer)
    download_wdpa(storage, gdf_buffer)
    download_power_networks(storage, gdf_buffer)
    download_pipelines(storage, gdf_buffer)

    # Process the DEM
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
