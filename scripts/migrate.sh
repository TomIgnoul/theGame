#!/usr/bin/env bash
set -euo pipefail

# Always resolve repo root (scripts/..)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SQL_FILE="$ROOT_DIR/db/migrations/001_init.sql"

if [[ ! -f "$SQL_FILE" ]]; then
  echo "[migrate] ERROR: missing $SQL_FILE"
  exit 1
fi

echo "[migrate] running $SQL_FILE"

docker exec -i thegame-postgres psql \
  -U thegame \
  -d thegame \
  -v ON_ERROR_STOP=1 \
  < "$SQL_FILE"

echo "[migrate] done"
