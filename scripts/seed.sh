#!/usr/bin/env bash
set -euo pipefail

echo "[seed] inserting minimal POIs into app.pois (idempotent)"

docker exec -i thegame-postgres psql \
  -U thegame \
  -d thegame \
  -v ON_ERROR_STOP=1 \
  << 'SQL'
INSERT INTO app.pois (source_id, name, lat, lng, theme, short_description, practical_info)
VALUES
  ('seed-001', 'Hidden Gem 1', 50.8466, 4.3528, 'Culture', 'Seed POI for M2', NULL),
  ('seed-002', 'Hidden Gem 2', 50.8450, 4.3600, 'Food',    'Seed POI for M2', 'Try the local spot')
ON CONFLICT (source_id) DO NOTHING;
SQL

echo "[seed] done"
