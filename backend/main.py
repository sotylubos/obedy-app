"""
FastAPI backend pro Obědovou appku.

Spuštění:
    uvicorn main:app --reload --port 8000

Pak otevři http://localhost:8000 v prohlížeči.
"""

import time
import logging
from pathlib import Path
from dataclasses import asdict
from typing import Dict, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from restaurants import RESTAURANTS
from scraper import fetch_menu
import votes

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("main")

app = FastAPI(title="Obědová appka")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE: Dict[str, tuple] = {}  # { restaurant_id: (timestamp, RestaurantMenu) }
CACHE_TTL_SECONDS = 3 * 60 * 60  # 3 hodiny


def get_menu_cached(restaurant: dict):
    now = time.time()
    cached = CACHE.get(restaurant["id"])
    if cached and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    menu = fetch_menu(restaurant)
    CACHE[restaurant["id"]] = (now, menu)
    return menu


@app.get("/api/menus")
def api_menus(x_voter_id: Optional[str] = Header(default=None)):
    if not RESTAURANTS:
        return {"restaurants": [], "note": "V restaurants.py zatím není žádná restaurace."}

    counts = votes.get_counts()
    my_vote = votes.get_voter_choice(x_voter_id) if x_voter_id else None

    result = []
    for r in RESTAURANTS:
        menu = get_menu_cached(r)
        data = asdict(menu)
        data["votes"] = counts.get(r["id"], 0)
        data["my_vote"] = r["id"] == my_vote
        result.append(data)

    return {"restaurants": result}


@app.post("/api/menus/refresh")
def api_refresh():
    for r in RESTAURANTS:
        CACHE.pop(r["id"], None)
    return {"status": "cache smazána, další /api/menus stáhne čerstvá data"}


@app.get("/api/votes")
def api_votes(x_voter_id: Optional[str] = Header(default=None)):
    return {
        "counts": votes.get_counts(),
        "my_vote": votes.get_voter_choice(x_voter_id) if x_voter_id else None,
    }


class VoteRequest(BaseModel):
    restaurant_id: str


@app.post("/api/vote")
def api_vote(body: VoteRequest, x_voter_id: Optional[str] = Header(default=None)):
    if not x_voter_id:
        raise HTTPException(status_code=400, detail="Chybí hlavička X-Voter-Id")

    valid_ids = {r["id"] for r in RESTAURANTS}
    if body.restaurant_id not in valid_ids:
        raise HTTPException(status_code=404, detail="Neznámá restaurace")

    my_vote = votes.toggle_vote(x_voter_id, body.restaurant_id)
    return {"counts": votes.get_counts(), "my_vote": my_vote}


# --- Servírování frontendu ---------------------------------------------
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))
