from spai.data.satellite import download_satellite_imagery
from spai.data.hidrology import download_waterways
from spai.data.utilities import (
    download_roads,
    download_buildings,
    download_power_networks,
    download_pipelines,
)
from spai.storage import Storage
from spai.config import SPAIVars
import geopandas as gpd

storage = Storage()["data"]
vars = SPAIVars()


def create_buffer(gdf: gpd.GeoDataFrame, buffer_size: int) -> gpd.GeoDataFrame:
    """
    Create a buffer around a GeoDataFrame.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame to buffer.
    buffer_size : int
        The buffer size in meters.

    Returns
    -------
    GeoDataFrame
        The GeoDataFrame with the buffer.
    """
    if not gdf.crs:
        gdf = gdf.set_crs("EPSG:4326")
    gdf_3857 = gdf.to_crs("EPSG:3857")
    # Create a new geodataframe with the buffer
    gdf_3857["geometry"] = gdf_3857.geometry.buffer(buffer_size)
    gdf = gdf_3857.to_crs("EPSG:4326")

    return gdf


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
    # Buffer 5 km to download the data
    gdf_buffer = create_buffer(gdf, 5000)
    download_waterways(storage, gdf_buffer)
    download_roads(storage, gdf_buffer)
    download_buildings(storage, gdf_buffer)
    download_power_networks(storage, gdf_buffer)
    download_pipelines(storage, gdf_buffer)
