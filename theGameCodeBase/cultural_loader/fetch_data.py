import requests
import psycopg
from paginate import page_through
from requests.exceptions import HTTPError, RequestException
from transform import transform_record
from api_list import BASE_URL, DATASETS  

DB_CONNINFO = "dbname=thegame user=admin password=W@cthw00rd host=localhost port=5432"


def insert_cultural_site(clean):
    """Insert one cleaned record into PostgreSQL using psycopg3."""
    try:
        with psycopg.connect(DB_CONNINFO) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO cultural_sites
                    (description_nl, description_fr, address_nl, address_fr, postal_code, city_nl, city_fr,
                     google_maps_url, google_street_view_url, longitude, latitude)
                    VALUES (%(description_nl)s, %(description_fr)s, %(address_nl)s, %(address_fr)s,
                            %(postal_code)s, %(city_nl)s, %(city_fr)s, %(google_maps_url)s,
                            %(google_street_view_url)s, %(longitude)s, %(latitude)s)
                """, clean)
                conn.commit()
        print("Inserted:", clean.get("description_nl") or clean.get("description_fr"))
    except Exception as e:
        print("Insert failed:", e)


def fetch(url, params=None):
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except HTTPError as http_err:
        print(f"[HTTP error] {url}: {http_err}")
    except RequestException as net_err:
        print(f"[Network error] {url}: {net_err}")
    except ValueError as json_err:
        print(f"[JSON parse error] {url}: {json_err}")
    return None


def fetch_page(dataset: str, limit: int, offset: int) -> list[dict]:
    """Fetch a single page for a given dataset."""
    url = f"{BASE_URL}/api/explore/v2.1/catalog/datasets/{dataset}/records"
    data = fetch(url, params={"limit": limit, "offset": offset})
    if data is None:
        return []
    return data.get("results", [])


if __name__ == "__main__":
    for name, dataset in DATASETS.items():
        print(f"\n=== Fetching dataset: {name} ===")
        url = f"{BASE_URL}/api/explore/v2.1/catalog/datasets/{dataset}/records"
        payload = fetch(url, params={"limit": 5})
        if payload is None:
            print(f"Fetch failed for {name}")
            continue

        results = payload.get("results", [])
        print(f" Fetched {len(results)} records for {name}")

        # process first few results
        for rec in results[:3]:
            clean = transform_record(rec)
            insert_cultural_site(clean)
            rid = rec.get("id", "no-id")
            fields = rec.get("fields", rec)
            title = fields.get("beschrijving") or fields.get("description") or "(no title)"
            print(f"   → id={rid} title={title}")

