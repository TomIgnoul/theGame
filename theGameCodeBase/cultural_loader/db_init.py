import psycopg

DB_CONNINFO = "dbname=thegame user=admin password=W@cthw00rd host=localhost port=5432"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS public.cultural_sites (
    id SERIAL PRIMARY KEY,
    description_nl TEXT,
    description_fr TEXT,
    address_nl TEXT,
    address_fr TEXT,
    postal_code TEXT,
    city_nl TEXT,
    city_fr TEXT,
    google_maps_url TEXT,
    google_street_view_url TEXT,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION
);
"""

with psycopg.connect(DB_CONNINFO) as conn:
    with conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)
