import requests
import psycopg
import logging  # <-- new import
from paginate import page_through
from requests.exceptions import HTTPError, RequestException
from transform import transform_record
from api_list import BASE_URL, DATASETS

DB_CONNINFO = "dbname=thegame user=admin password=W@cthw00rd host=localhost port=5432"

# ---------------------------------------------------------------------------
# Logging configuration
#
# This sets up a basic log format that shows the timestamp, log level, and
# message. INFO level is a good default to start with. You can switch to
# DEBUG for more detail or WARNING/ERROR to reduce output.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)

def insert_cultural_site(clean: dict) -> None:
    """Insert one cleaned record into PostgreSQL using psycopg3,
    with progress logs and a connection timeout."""
    # Determine a short title for logging purposes
    title = clean.get("description_nl") or clean.get("description_fr") or "(no title)"
    try:
        # Log that we’re about to connect to the database
        logger.info("Connecting to database to insert: %s", title)

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

        logger.info("Inserted record: %s", title)
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

# ---------------------------------------------------------------------------
# Main script
#
def main() -> None:
    logger.info("Starting cultural sites data load")
    try:
        for name, dataset in DATASETS.items():
            logger.info("Fetching dataset: %s", name)
            url = f"{BASE_URL}/api/explore/v2.1/catalog/datasets/{dataset}/records"
            payload = fetch(url, params={"limit": 5})
            if payload is None:
                logger.warning("Fetch failed for dataset %s", name)
                continue

            results = payload.get("results", [])
            logger.info("Fetched %d records for %s", len(results), name)

            # Process first few results
        for rec in results[:3]:
            clean = transform_record(rec)
            insert_cultural_site(clean)
            rid = rec.get("id", "no-id")
            fields = rec.get("fields", rec)
            title = fields.get("beschrijving") or fields.get("description") or "(no title)"
            logger.info("Processed record id=%s title=%s", rid, title)
        logger.info("Cultural sites data load finished successfully")
    except Exception:
        # Catch any unanticipated exception and log with full traceback
        logger.exception("Unhandled exception during data load")
        raise

if __name__ == "__main__":
    main()