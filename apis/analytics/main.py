"""
Analytics API
"""

import argparse

import uvicorn
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from spai.storage import Storage
from spai.config import SPAIVars
import geopandas as gpd

app = FastAPI(title="analytics")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/{file}")
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
        print(file)
        if not storage.exists(f"{file}.geojson"):
            print("no")
            return {}
        analytics = storage.read(f"{file}.geojson")
        analytics = analytics.to_json()
        # convert to dict
        analytics = json.loads(analytics)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# need this to run in background
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
