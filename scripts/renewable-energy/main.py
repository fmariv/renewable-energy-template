from spai.storage import Storage
from spai.config import SPAIVars
from spai.logging.log import log_inputs, log_results, Result

from src.downloads import (
    download_terrain_data,
    download_geophysical_data,
    download_infrastructure_data,
)
from src.suitable_areas import find_suitable_areas
from src.status_registry import (
    BUILDING,
    ERROR,
    READY,
    WARNING,
    set_status,
)
import geopandas as gpd
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)

storage = Storage()["data"]
vars = SPAIVars()


def main():
    """Main function that executes the workflow"""
    storage = Storage()["data"]
    vars = SPAIVars()
    aoi = vars["AOI"]
    gdf = gpd.GeoDataFrame.from_features(aoi, crs="EPSG:4326")

    log_inputs(vars["AOI"])

    try:
        set_status(
            storage,
            BUILDING,
            "Data is being downloaded and processed...",
        )

        set_status(storage, BUILDING, "Downloading terrain data...")
        download_terrain_data(storage, gdf)
        if not storage.exists("dem.tif") or not storage.exists("land_cover.tif"):
            set_status(
                storage,
                WARNING,
                "Terrain data incomplete — DEM or land cover missing",
            )

        set_status(storage, BUILDING, "Downloading geophysical data...")
        download_geophysical_data(storage, gdf)
        if not storage.exists("protected_areas.geojson"):
            set_status(
                storage,
                WARNING,
                "No protected areas found",
            )

        set_status(storage, BUILDING, "Downloading infrastructure data...")
        download_infrastructure_data(storage, gdf)
        if not storage.exists("roads.geojson"):
            set_status(
                storage,
                WARNING,
                "No roads found",
            )

        set_status(storage, BUILDING, "Finding suitable areas...")
        suitable_areas = find_suitable_areas(storage, gdf)

        suitable_areas_utm = suitable_areas.to_crs(suitable_areas.estimate_utm_crs())
        area_km2 = 0.0
        if suitable_areas_utm is not None and not suitable_areas_utm.empty:
            area_km2 = round(
                suitable_areas_utm.to_crs(epsg=3857).geometry.area.sum() / 1e6, 2
            )

        log_results(
            [
                Result(label="Suitable area", value=area_km2, unit="km2"),
                Result(
                    label="Number of suitable locations",
                    value=(
                        len(suitable_areas_utm)
                        if suitable_areas_utm is not None
                        else 0
                    ),
                ),
            ]
        )

        if suitable_areas is None or suitable_areas.empty:
            set_status(
                storage,
                READY,
                "Pipeline completed — no suitable areas found",
            )
        else:
            set_status(storage, READY, "Pipeline completed successfully")

    except Exception as e:
        logger.exception("Pipeline failed")
        set_status(storage, ERROR, str(e))
        raise


if __name__ == "__main__":
    main()
