import os
import time
from collections import defaultdict, deque
from typing import Literal, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from psycopg import connect
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import JSONResponse

app = FastAPI(title="theGame API", version="0.1.0")

# -------------------------
# Rate limiting (in-memory)
# -------------------------
RATE_LIMITS = {
    "/routes/generate": (3, 60),  # 3 req per 60s per IP
    "/chat/stop": (10, 60),       # 10 req per 60s per IP
}

_hits = defaultdict(deque)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path

    if request.method == "POST" and path in RATE_LIMITS:
        limit, window = RATE_LIMITS[path]
        ip = request.client.host if request.client else "unknown"
        key = f"{ip}:{path}"

        now = time.time()
        q = _hits[key]

        # drop old hits outside the window
        while q and (now - q[0]) > window:
            q.popleft()

        if len(q) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Even wachten en opnieuw proberen."},
            )

        q.append(now)

    return await call_next(request)

# -------------------------
# Health
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------
# POIs
# -------------------------
@app.get("/pois")
def list_pois():
    db_url = os.environ["DATABASE_URL"]

    with connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, source_id, name, lat, lng, theme, short_description, practical_info
                FROM app.pois
                ORDER BY id ASC
                """
            )
            rows = cur.fetchall()

    return [
        {
            "id": r[0],
            "source_id": r[1],
            "name": r[2],
            "lat": r[3],
            "lng": r[4],
            "theme": r[5],
            "short_description": r[6],
            "practical_info": r[7],
        }
        for r in rows
    ]

# -------------------------
# Routes (stub)
# -------------------------
Theme = Literal["War", "Museum", "Streetart", "Food", "Culture"]

class RouteGenerateRequest(BaseModel):
    theme: Theme
    distance_km: Optional[float] = Field(default=None, ge=0.1)
    duration_min: Optional[int] = Field(default=None, ge=1)

class RouteStop(BaseModel):
    stop_number: int
    poi_id: int
    name: str
    lat: float
    lng: float

class RouteGenerateResponse(BaseModel):
    route_id: str
    theme: Theme
    distance_km: Optional[float]
    duration_min: Optional[int]
    coordinates: list[dict]  # [{"lat":..,"lng":..}, ...]
    stops: list[RouteStop]

@app.post("/routes/generate", response_model=RouteGenerateResponse)
def generate_route(req: RouteGenerateRequest):
    db_url = os.environ["DATABASE_URL"]

    # Minimal stub: pick up to 5 POIs matching the theme
    with connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, lat, lng
                FROM app.pois
                WHERE theme = %s
                ORDER BY id ASC
                LIMIT 5
                """,
                (req.theme,),
            )
            rows = cur.fetchall()

    stops = [
        {
            "stop_number": i + 1,
            "poi_id": r[0],
            "name": r[1],
            "lat": r[2],
            "lng": r[3],
        }
        for i, r in enumerate(rows)
    ]

    # Dummy polyline: connect stops in order
    coordinates = [{"lat": s["lat"], "lng": s["lng"]} for s in stops]

    return {
        "route_id": str(uuid4()),
        "theme": req.theme,
        "distance_km": req.distance_km,
        "duration_min": req.duration_min,
        "coordinates": coordinates,
        "stops": stops,
    }

# -------------------------
# Chat per stop (stub)
# -------------------------
class ChatStopRequest(BaseModel):
    route_id: str
    stop_number: int = Field(ge=1)
    poi_id: int
    message: str

class ChatStopResponse(BaseModel):
    header: str
    reply: str

@app.post("/chat/stop", response_model=ChatStopResponse)
def chat_stop(req: ChatStopRequest):
    # 500 chars cap (locked)
    if len(req.message) > 500:
        raise HTTPException(status_code=400, detail="Message too long (max 500 chars).")

    db_url = os.environ["DATABASE_URL"]

    # Fetch POI name for strict header format
    with connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM app.pois WHERE id = %s", (req.poi_id,))
            row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="POI not found.")

    poi_name = row[0]
    header = f"Stop {req.stop_number} — {poi_name}"

    # Placeholder reply (later: LLM call with stop context)
    reply = f"(stub) Story for {poi_name}. You said: {req.message}"

    return {"header": header, "reply": reply}
