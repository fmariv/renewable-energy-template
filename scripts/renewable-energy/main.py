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

from utils import create_buffer
from dem import process_dem

storage = Storage()["data"]
vars = SPAIVars()


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

    # Process the DEM
    process_dem(storage)
