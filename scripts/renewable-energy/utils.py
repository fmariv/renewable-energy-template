"""
Utility functions for the renewable energy analysis.
"""

import geopandas as gpd


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
