import requests
import psycopg
import logging  # <-- new import
from paginate import page_through
from requests.exceptions import HTTPError, RequestException
from transform import transform_record
from api_list import BASE_URL, DATASETS
from logging_config import setup_logging

"""
fetch_data.py – Load cultural datasets into PostgreSQL with progress logging.

This script downloads cultural datasets from the Brussels Open Data portal and inserts
the transformed records into a PostgreSQL database. It is designed to be used as a
data loader, fetching all pages of each dataset, transforming each record via
`transform_record()`, and inserting them into the `cultural_sites` table.

Main steps:
1. Define the datasets to fetch in api_list.py.
2. Use the `page_through()` helper to paginate through each dataset.
3. For each record, call `transform_record()` to normalize the fields.
4. Insert cleaned records into PostgreSQL with `insert_cultural_site()`, committing
   after each insert to provide durable checkpoints.
5. Log progress at INFO level so that long runs show what page and dataset are being processed,
   with detailed per-record logs available at DEBUG level.

Prerequisites:
- A running PostgreSQL instance accessible via the `DB_CONNINFO` connection string.
- A table named `cultural_sites` with columns corresponding to the fields inserted.
- Internet access to reach the Brussels Open Data API.

Usage:
    python fetch_data.py

Adjust the `per_page` parameter in `process_dataset()` if you need smaller or larger pages.
See the README for database setup instructions.
"""


DB_CONNINFO = "dbname=thegame user=admin password=W@cthw00rd host=localhost port=5432"

setup_logging()
logger = logging.getLogger(__name__)

def insert_cultural_site(clean: dict) -> None:
    """Insert one cleaned record into PostgreSQL using psycopg3,
    with progress logs and a connection timeout."""
    # Determine a short title for logging purposes
    title = clean.get("description_nl") or clean.get("description_fr") or "(no title)"
    try:
        # Log that we’re about to connect to the database
        logger.debug("Connecting to database to insert: %s", title)

        # Append a connect_timeout parameter so psycopg won’t wait forever
        conninfo_with_timeout = DB_CONNINFO + " connect_timeout=10"

        with psycopg.connect(conninfo_with_timeout) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO cultural_sites
                    (description_nl, description_fr, address_nl, address_fr,
                     postal_code, city_nl, city_fr, google_maps_url,
                     google_street_view_url, longitude, latitude)
                    VALUES (%(description_nl)s, %(description_fr)s,
                            %(address_nl)s, %(address_fr)s,
                            %(postal_code)s, %(city_nl)s, %(city_fr)s,
                            %(google_maps_url)s, %(google_street_view_url)s,
                            %(longitude)s, %(latitude)s)
                """, clean)
                conn.commit()

        #logger.info("Inserted record: %s", title)
        logger.debug("Inserted record: %s", title)
    except Exception as e:
        # Log the error with full traceback to diagnose what went wrong
        logger.error("Insert failed for %s: %s", title, e, exc_info=True)

def fetch(url: str, params: dict | None = None) -> dict | None:
    """Fetch JSON data from the given URL with optional query parameters.

    On success returns a parsed JSON object (a dict), otherwise returns None.
    Errors are logged rather than printed.
    """
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except HTTPError as http_err:
        logger.error("HTTP error for %s: %s", url, http_err)
    except RequestException as net_err:
        logger.error("Network error for %s: %s", url, net_err)
    except ValueError as json_err:
        logger.error("JSON parse error for %s: %s", url, json_err)
    return None

def fetch_page(dataset: str, limit: int, offset: int) -> list[dict]:
    """Fetch a single page for a given dataset."""
    url = f"{BASE_URL}/api/explore/v2.1/catalog/datasets/{dataset}/records"
    data = fetch(url, params={"limit": limit, "offset": offset})
    if data is None:
        return []
    return data.get("results", [])

def process_dataset(name: str, dataset: str, per_page: int = 100) -> None:
    """
    Fetch all pages of a dataset from the Brussels Open Data API and insert the records.

    This helper uses the `page_through` generator to request consecutive pages of
    `per_page` records until no more data is available. For each page it logs the page
    number and record count, transforms each record via `transform_record()`, and then
    inserts it into PostgreSQL with `insert_cultural_site()`.

    Args:
        name: Friendly name of the dataset (e.g. "street_art").
        dataset: API identifier for the dataset (e.g. "parcours_street_art").
        per_page: Number of records to request per page. Adjust based on network speed
                  and memory. Defaults to 100.

    Logs:
        INFO messages for page start/completion and per-record processing.
        Errors are propagated from `insert_cultural_site()` and logged there.
    """
    def fetch_fn(limit: int, offset: int) -> list[dict]:
        # Adapt fetch_page() to the signature expected by page_through().
        return fetch_page(dataset, limit, offset)

    for page_no, items in enumerate(page_through(fetch_fn, per_page=per_page), start=1):
        if not items:
            break
        logger.info("Dataset %s: processing page %d with %d records", name, page_no, len(items))
        for rec in items:
            clean = transform_record(rec)
            insert_cultural_site(clean)
            rid = rec.get("id", "no-id")
            logger.debug("Processed record id=%s", rid)
            fields = rec.get("fields", rec)
            title = (
                fields.get("beschrijving")
                or fields.get("description")
                or fields.get("name")
                or fields.get("nom")
                or fields.get("title")
                or "(no title)"
            )

            logger.debug("Processed record id=%s title=%s", rid, title)
        logger.debug("Dataset %s: finished page %d", name, page_no)

# ---------------------------------------------------------------------------
# Main script

def main() -> None:
    logger.info("Starting cultural sites data load")
    try:
        for name, dataset in DATASETS.items():
            logger.info("Beginning processing of dataset: %s", name)
            process_dataset(name, dataset, per_page=100)
            logger.info("Completed processing of dataset: %s", name)

        logger.info("Cultural sites data load finished successfully")
    except Exception:
        logger.exception("Unhandled exception during data load")
        raise


if __name__ == "__main__":
    main()