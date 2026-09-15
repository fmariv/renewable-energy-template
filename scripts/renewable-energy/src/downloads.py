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
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def _try_osm_download(label: str, fn: Callable[[], None]) -> Optional[str]:
    """Run an OSM download; on failure log and return the layer label, else None."""
    try:
        fn()
        return None
    except Exception as exc:
        logger.warning("OSM download failed for %s (continuing): %s", label, exc)
        return label


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


def download_geophysical_data(storage, gdf: gpd.GeoDataFrame) -> list[str]:
    """
    Downloads geophysical data (waterways and protected areas).

    OSM/network failures are soft: the layer is skipped and its name is returned
    so the caller can mark a Warning without stopping the pipeline.
    """
    logger.info("Downloading geophysical data...")
    gdf_buffer = create_buffer(gdf, 5000)
    failed: list[str] = []

    skipped = _try_osm_download(
        "waterways", lambda: download_waterways(storage, gdf_buffer)
    )
    if skipped:
        failed.append(skipped)

    skipped = _try_osm_download(
        "protected_areas",
        lambda: download_protected_areas(storage, gdf_buffer),
    )
    if skipped:
        failed.append(skipped)

    if failed:
        logger.warning("Geophysical download finished with skips: %s", ", ".join(failed))
    else:
        logger.info("Geophysical data downloaded successfully")
    return failed


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
    """
    logger.info("Downloading pipelines data...")
    lines_gdf = load_pipelines(aoi, source, query, crs)
    lines_gdf = lines_gdf.map(lambda x: x if not isinstance(x, list) else str(x))
    if not lines_gdf.empty:
        storage.create(lines_gdf, name=name)
    logger.info("Pipelines data downloaded successfully")


def download_infrastructure_data(storage, gdf: gpd.GeoDataFrame) -> list[str]:
    """
    Downloads infrastructure data (roads, buildings, power networks, pipelines).

    OSM/network failures are soft: each failed layer is skipped and listed in
    the returned list so the pipeline can continue with a Warning.
    """
    gdf_buffer = create_buffer(gdf, 5000)
    failed: list[str] = []

    for label, fn in (
        ("roads", lambda: download_roads(storage, gdf_buffer)),
        ("buildings", lambda: download_buildings(storage, gdf_buffer)),
        ("power_networks", lambda: download_power_networks(storage, gdf_buffer)),
        ("pipelines", lambda: download_pipelines(storage, gdf_buffer)),
    ):
        skipped = _try_osm_download(label, fn)
        if skipped:
            failed.append(skipped)

    if failed:
        logger.warning(
            "Infrastructure download finished with skips: %s", ", ".join(failed)
        )
    else:
        logger.info("Infrastructure data downloaded successfully")
    return failed
