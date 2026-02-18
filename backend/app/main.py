import os
from fastapi import FastAPI
from psycopg import connect

app = FastAPI(title="theGame API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


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
