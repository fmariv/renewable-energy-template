from spai.storage import Storage
from spai.config import SPAIVars

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
