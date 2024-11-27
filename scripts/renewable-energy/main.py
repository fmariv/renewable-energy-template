from spai.data.satellite import download_satellite_imagery
from spai.data.hidrology import download_waterways
from spai.data.utilities import (
    download_roads,
    download_buildings,
    download_power_networks,
    download_pipelines,
)
from spai.data.ecosystems import download_protected_areas
from spai.storage import Storage
from spai.config import SPAIVars
import geopandas as gpd
import pandas as pd

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


def download_terrain_data(storage, gdf: gpd.GeoDataFrame) -> tuple:
    """
    Downloads terrain data (DEM and land cover)

    Parameters
    ----------
    storage : Storage
        Storage object to save the downloaded data
    gdf : GeoDataFrame
        GeoDataFrame with the area of interest

    Returns
    -------
    tuple
        (dem, land_cover) downloaded files
    """
    dem = download_satellite_imagery(
        storage, gdf, collection="cop-dem-glo-30", name="dem.tif"
    )
    lc = download_satellite_imagery(
        storage, gdf, date="2021", collection="esa-worldcover", name="land_cover.tif"
    )
    return dem, lc


def download_geophysical_data(storage, gdf: gpd.GeoDataFrame) -> None:
    """
    Downloads geophysical data (waterways and protected areas)

    Parameters
    ----------
    storage : Storage
        Storage object to save the downloaded data
    gdf : GeoDataFrame
        GeoDataFrame with the area of interest
    """
    gdf_buffer = create_buffer(gdf, 5000)
    download_waterways(storage, gdf_buffer)
    download_protected_areas(storage, gdf_buffer)


def download_infrastructure_data(storage, gdf: gpd.GeoDataFrame) -> None:
    """
    Downloads infrastructure data (roads, buildings, power networks, pipelines)

    Parameters
    ----------
    storage : Storage
        Storage object to save the downloaded data
    gdf : GeoDataFrame
        GeoDataFrame with the area of interest
    """
    gdf_buffer = create_buffer(gdf, 5000)
    download_roads(storage, gdf_buffer)
    download_buildings(storage, gdf_buffer)
    download_power_networks(storage, gdf_buffer)
    download_pipelines(storage, gdf_buffer)


def find_suitable_areas(storage, aoi_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Finds suitable areas within AOI that are:
    - NOT within protected areas
    - Within 500m of relevant infrastructure (roads, power networks)

    Parameters
    ----------
    storage : Storage
        Storage object where the data is saved
    aoi_gdf : GeoDataFrame
        GeoDataFrame with the area of interest

    Returns
    -------
    GeoDataFrame
        Areas that meet the criteria
    """
    # Load all required layers
    protected_areas, roads, power_networks, pipelines = None, None, None, None
    if storage.exists("protected_areas.geojson"):
        protected_areas = storage.read("protected_areas.geojson")
    if storage.exists("roads.geojson"):
        roads = storage.read("roads.geojson")
    if storage.exists("power_lines.geojson"):
        power_networks = storage.read("power_lines.geojson")
    if storage.exists("pipelines.geojson"):
        pipelines = storage.read("pipelines.geojson")

    # Ensure all layers are in the same CRS
    layers = [protected_areas, roads, power_networks, pipelines]
    for layer in layers:
        if layer is not None:
            if layer.crs is None:
                layer = layer.set_crs("EPSG:4326")
            elif layer.crs != "EPSG:4326":
                layer = layer.to_crs("EPSG:4326")

    # Create infrastructure buffer (500m)
    infrastructure_layers = [roads, power_networks, pipelines]
    infrastructure_buffer = gpd.GeoDataFrame(geometry=[], crs=aoi_gdf.crs)

    for layer in infrastructure_layers:
        if layer is not None and not layer.empty:
            buffer = create_buffer(layer, 500)
            infrastructure_buffer = pd.concat([infrastructure_buffer, buffer])

    # Dissolve all infrastructure buffers into a single polygon
    if not infrastructure_buffer.empty:
        infrastructure_buffer = infrastructure_buffer.dissolve()

    # Find areas that are NOT protected
    if not protected_areas.empty:
        non_protected = aoi_gdf.overlay(protected_areas, how="difference")
    else:
        non_protected = aoi_gdf

    # Find intersection with infrastructure buffer
    if not infrastructure_buffer.empty:
        suitable_areas = non_protected.overlay(
            infrastructure_buffer, how="intersection"
        )
    else:
        suitable_areas = gpd.GeoDataFrame(geometry=[], crs=aoi_gdf.crs)

    if not suitable_areas.empty:
        storage.create(suitable_areas, "suitable_areas.geojson")


def main():
    """Main function that executes the workflow"""
    storage = Storage()["data"]
    vars = SPAIVars()
    aoi = vars["AOI"]
    gdf = gpd.GeoDataFrame.from_features(aoi, crs="EPSG:4326")

    # Download all required layers
    # Terrain
    download_terrain_data(storage, gdf)
    # Geophysical
    download_geophysical_data(storage, gdf)
    # Infrastructure
    download_infrastructure_data(storage, gdf)
    # Find suitable areas
    find_suitable_areas(storage, gdf)


if __name__ == "__main__":
    main()
