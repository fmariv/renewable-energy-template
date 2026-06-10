from spai.storage import Storage
from spai.config import SPAIVars
from spai.logging.log import log_inputs, log_results, Result

from src.downloads import (
    download_terrain_data,
    download_geophysical_data,
    download_infrastructure_data,
)
from src.suitable_areas import find_suitable_areas
import geopandas as gpd

storage = Storage()["data"]
vars = SPAIVars()


def main():
    """Main function that executes the workflow"""
    storage = Storage()["data"]
    vars = SPAIVars()
    aoi = vars["AOI"]
    gdf = gpd.GeoDataFrame.from_features(aoi, crs="EPSG:4326")

    log_inputs(vars["AOI"])

    # Download all required layers
    # Terrain
    download_terrain_data(storage, gdf)
    # Geophysical
    download_geophysical_data(storage, gdf)
    # Infrastructure
    download_infrastructure_data(storage, gdf)
    # Find suitable areas
    suitable_areas = find_suitable_areas(storage, gdf)


    suitable_areas_utm = suitable_areas.to_crs(suitable_areas.estimate_utm_crs())
    area_km2 = 0.0
    if suitable_areas_utm is not None and not suitable_areas_utm.empty:
        area_km2 = round(
            suitable_areas_utm.to_crs(epsg=3857).geometry.area.sum() / 1e6, 2
        )

    log_results([
        Result(label="Suitable area", value=area_km2, unit="km2"),
        Result(label="Number of suitable locations", value=len(suitable_areas_utm) if suitable_areas_utm is not None else 0),
    ])


if __name__ == "__main__":
    main()
