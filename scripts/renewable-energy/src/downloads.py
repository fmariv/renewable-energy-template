import logging
import geopandas as gpd
from spai.data.satellite import download_satellite_imagery
from spai.data.hidrology import download_waterways
from spai.data.utilities import (
    download_roads,
    download_buildings,
    load_power_networks,
    load_pipelines,
)
from spai.data.ecosystems import download_protected_areas
from .utilities import create_buffer
from typing import Any, Optional

logger = logging.getLogger(__name__)


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
    logger.info("Downloading terrain data...")
    dem = download_satellite_imagery(
        storage, gdf, collection="cop-dem-glo-30", name="dem.tif"
    )
    lc = download_satellite_imagery(
        storage, gdf, date="2021", collection="esa-worldcover", name="land_cover.tif"
    )
    logger.info("Terrain data downloaded successfully")
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
    logger.info("Downloading geophysical data...")
    gdf_buffer = create_buffer(gdf, 5000)
    download_waterways(storage, gdf_buffer)
    download_protected_areas(storage, gdf_buffer)
    logger.info("Geophysical data downloaded successfully")


def download_power_networks(
    storage,
    aoi: Any,
    line_name: Optional[str] = "power_lines.geojson",
    point_name: Optional[str] = "power_points.geojson",
    polygon_name: Optional[str] = "power_polygons.geojson",
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "power": ["line", "cable", "substation", "plant", "transformer"]
    },
    crs: Optional[str] = "EPSG:4326",
) -> None:
    """
    Download power network elements from OpenStreetMap for the given area of interest and separate them by geometry type.

    Parameters
    ----------
    aoi : Any
        The area of interest
    storage : BaseStorage
        The storage object
    line_name : str, optional
        The name of the file to store line geometries, by default "power_lines.geojson"
    point_name : str, optional
        The name of the file to store point geometries, by default "power_points.geojson"
    polygon_name : str, optional
        The name of the file to store polygon geometries, by default "power_polygons.geojson"
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes power lines, cables, substations, plants, and transformers.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)
    """
    final_power_networks_gdf = load_power_networks(aoi, source, query, crs)

    logger.info("Downloading power networks data...")
    lines_gdf = final_power_networks_gdf[
        final_power_networks_gdf.geometry.type.isin(("LineString", "MultiLineString"))
    ]
    points_gdf = final_power_networks_gdf[
        final_power_networks_gdf.geometry.type.isin(("Point", "MultiPoint"))
    ]
    polygons_gdf = final_power_networks_gdf[
        final_power_networks_gdf.geometry.type.isin(("Polygon", "MultiPolygon"))
    ]

    lines_gdf = lines_gdf.map(lambda x: x if not isinstance(x, list) else str(x))
    points_gdf = points_gdf.map(lambda x: x if not isinstance(x, list) else str(x))
    polygons_gdf = polygons_gdf.map(
        lambda x: x if not isinstance(x, list) else str(x)
    )

    if not lines_gdf.empty:
        storage.create(lines_gdf, name=line_name)
    if not points_gdf.empty:
        storage.create(points_gdf, name=point_name)
    if not polygons_gdf.empty:
        storage.create(polygons_gdf, name=polygon_name)
    logger.info("Power networks data downloaded successfully")


def download_pipelines(
    storage,
    aoi: Any,
    name: Optional[str] = "pipelines_lines.geojson",
    source: Optional[str] = "osm",
    query: Optional[dict] = {
        "man_made": ["pipeline"],
        "pipeline": ["oil", "gas", "water", "sewage", "heat"],
    },
    crs: Optional[str] = "EPSG:4326",
) -> None:
    """
    Download pipeline elements from OpenStreetMap for the given area of interest.

    Parameters
    ----------
    aoi : Any
        The area of interest
    storage : BaseStorage
        The storage object
    name : str, optional
        The name of the file to store line geometries, by default "pipelines_lines.geojson"
    source : str, optional
        The data source, by default "osm"
    query : dict, optional
        The query to use, by default includes pipelines for oil, gas, water, sewage, and heat.
    crs : str, optional
        The coordinate reference system to use, by default WGS84 (EPSG:4326)
    """
    logger.info("Downloading pipelines data...")
    lines_gdf = load_pipelines(aoi, source, query, crs)
    lines_gdf = lines_gdf.map(lambda x: x if not isinstance(x, list) else str(x))
    if not lines_gdf.empty:
        storage.create(lines_gdf, name=name)
    logger.info("Pipelines data downloaded successfully")


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