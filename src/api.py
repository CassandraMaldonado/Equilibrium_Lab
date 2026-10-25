# Helps for the decision brief and dashboard from the analysis. 
# The API also makes the results easy to inspect or reuse elsewhere.

from functools import lru_cache
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .analysis import analyze

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
app = FastAPI(title="Equilibrium Lab API", version="0.1.0")


@lru_cache(maxsize=32)
def _brief(seed: int, zones: int):
    return analyze(seed, zones)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/brief")
def brief(seed: int = Query(29, ge=0, le=1_000_000), zones: int = Query(18, ge=8, le=50)):
    return _brief(seed, zones)


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


app.mount("/static", StaticFiles(directory=WEB), name="static")


def run():
    import uvicorn

    uvicorn.run("equilibrium_lab.api:app", host="127.0.0.1", port=8000)

