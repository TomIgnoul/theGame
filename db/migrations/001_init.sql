-- Schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS app;

-- Theme constraint (TEXT + CHECK)
-- We gebruiken TEXT + CHECK zoals design locked.
CREATE TABLE IF NOT EXISTS app.pois (
  id BIGSERIAL PRIMARY KEY,
  source_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  lat DOUBLE PRECISION NOT NULL,
  lng DOUBLE PRECISION NOT NULL,
  theme TEXT NOT NULL CHECK (theme IN ('War','Museum','Streetart','Food','Culture')),
  short_description TEXT NOT NULL,
  practical_info TEXT NULL
);

CREATE TABLE IF NOT EXISTS app.routes (
  route_id UUID PRIMARY KEY,
  theme TEXT NOT NULL CHECK (theme IN ('War','Museum','Streetart','Food','Culture')),
  distance_km DOUBLE PRECISION NULL,
  duration_min INTEGER NULL,
  start_mode TEXT NULL,
  start_lat DOUBLE PRECISION NULL,
  start_lng DOUBLE PRECISION NULL,
  coordinates JSONB NOT NULL DEFAULT '[]'::jsonb,
  summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  started_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS app.route_stops (
  route_id UUID NOT NULL REFERENCES app.routes(route_id) ON DELETE CASCADE,
  stop_number INTEGER NOT NULL,
  poi_id BIGINT NOT NULL REFERENCES app.pois(id),
  name_snapshot TEXT NOT NULL,
  lat_snapshot DOUBLE PRECISION NOT NULL,
  lng_snapshot DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (route_id, stop_number)
);
