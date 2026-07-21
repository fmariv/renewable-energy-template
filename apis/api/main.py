"""
Analytics API
"""

import argparse
import json
import os
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from prometheus_fastapi_instrumentator import Instrumentator

import geopandas as gpd
import numpy as np

from spai.storage import Storage
from spai.config import SPAIVars
from spai.processing import read_raster
from spai.image.xyz import get_image_data, get_tile_data, ready_image
from spai.image.xyz.errors import ImageOutOfBounds


app = FastAPI(title="api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app=app)

storage = Storage()["data"]
vars = SPAIVars()


@app.get("/aoi")
def retrieve_aoi():
    return vars["AOI"]


@app.get("/aois/{scenario}")
def retrieve_aoi_id(scenario: str):
    aois = vars["AOI"]
    scenario = scenario.lower()
    # read the dict as geodataframe
    gdf = gpd.GeoDataFrame.from_features(aois)
    aoi = gdf[gdf["scenario"] == scenario]
    aoi_gdf = json.loads(aoi.to_json())

    return aoi_gdf


@app.get("/analytics/{file}")
async def analytics(file: str):
    """
    Return water quality analytics

    Parameters
    ----------
    file : str
        Name of analytics file

    Parameters
    ----------
    file : str
        Name of analytics file

    Returns
    -------
    analytics : dict
        Dictionary with water quality analytics

    Raises
    ------
    HTTPException
        If analytics file doesn't exist
    """
    try:
        if not storage.exists(f"{file}.geojson"):
            return {}
        analytics = storage.read(f"{file}.geojson")
        analytics = analytics.to_json()
        # convert to dict
        analytics = json.loads(analytics)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/images/")
def retrieve_images():
    """
    Return available images

    Returns
    -------
    images : list
        List of available images in tif format
    """
    return storage.list("*.tif")


@app.get("/images/{image}")
def check_image_exists(image: str):
    """
    Check if image exists

    Parameters
    ----------
    image : str
        Image name

    Returns
    -------
    exists : bool
        If image exists
    """
    path = storage.get_path(image)
    return os.path.exists(path)


@app.get("/images/{image}/{z}/{x}/{y}.png")
def retrieve_image_tile(
    image: str,
    z: int,
    x: int,
    y: int,
    bands: Optional[str] = "1",
    stretch: Optional[str] = "0,1",
    palette: Optional[str] = "viridis",
):
    """
    Return image tile

    Parameters
    ----------
    image : str
        Image name
    z : int
        Zoom level
    x : int
        Tile x coordinate
    y : int
        Tile y coordinate
    bands : str, optional
        Bands to retrieve, by default "1"
    stretch : str, optional
        Stretch to apply, by default "0,1"
    palette : str, optional
        Palette to use, by default "viridis"

    Returns
    -------
    tile : StreamingResponse
        Image tile

    Raises
    ------
    HTTPException
        If image is not found
    """
    image_path = storage.get_path(f"{image}")
    tile_size = (256, 256)
    if len(bands) == 1:
        bands = int(bands)
    else:
        bands = tuple([int(band) for band in bands.split(",")])
    stretch = tuple([float(v) for v in stretch.split(",")])
    try:
        tile = get_tile_data(image_path, (x, y, z), bands, tile_size)
        tile = get_image_data(tile, stretch, palette)
        image = ready_image(tile)
        return StreamingResponse(image, media_type="image/png")
    except ImageOutOfBounds as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)


@app.get("/dem")
def get_dem_min_max_values():
    """
    Get min and max values of the DEM

    Returns
    -------
    min_max_values : dict
        Dictionary with min and max values
    """
    ds, dem = read_raster("dem.tif", storage)
    min_value = float(np.min(dem))
    max_value = float(np.max(dem))
    return {"min": min_value, "max": max_value}


def _read_pipeline_status() -> dict:
    """Read pipeline_status.json from storage as a plain dict."""
    status_path = "pipeline_status.json"
    idle = {
        "status": "Idle",
        "message": "No pipeline run yet",
        "updated_at": None,
    }
    if not storage.exists(status_path):
        return idle
    try:
        with open(storage.get_path(status_path), encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "status" in data:
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return idle


@app.get("/pipeline/status")
def pipeline_status():
    """Current pipeline status registry from storage."""
    return _read_pipeline_status()


@app.get("/data_available")
def data_available():
    """Whether the pipeline has produced ready outputs."""
    pipeline = _read_pipeline_status()
    ready = pipeline.get("status") == "Ready"
    return {
        "status": "healthy",
        "data_available": ready,
        "data_status": "ready" if ready else "no_data",
        "pipeline_status": pipeline.get("status"),
        "message": pipeline.get("message"),
    }


@app.get("/health")
def health():
    return {"status": "ok"}

# need this to run in background
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
