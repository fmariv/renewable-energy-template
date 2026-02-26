import geopandas as gpd
import pandas as pd
from .utilities import create_buffer

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
    print("Finding suitable areas...")
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

    print("Suitable areas found successfully")