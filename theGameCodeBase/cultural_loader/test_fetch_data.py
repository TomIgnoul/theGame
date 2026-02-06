import requests
import psycopg
from paginate import page_through
from requests.exceptions import HTTPError, RequestException
from transform import transform_record
BASE_URL = "https://opendata.brussels.be"
DATASET = "bruxelles_lieux_culturels"
ENDPOINT = f"/api/explore/v2.1/catalog/datasets/{DATASET}/records"  
URLS =["/api/explore/v2.1/catalog/datasets/{DATASET}/records",  
]
URL = BASE_URL + ENDPOINT
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
        print("Inserted:", clean["description_nl"] or clean["description_fr"])
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

def fetch_page(limit: int, offset: int) -> list[dict]:
    data = fetch(URL, params={"limit": limit, "offset": offset})
    if data is None:
        return []
    return data.get("results",[])

payload = fetch(URL, params={"limit": 20})
if payload is None:
    print("Fetch failed — retry")
else:
    results = payload.get("results", [])
    print("Fetch succeeded.")
    print(f"Fetched {len(results)} records")

i=0
for i in (0,2,4):
    print("offset =", i) 
    payload = fetch(URL, params={"limit":2, "offset": i})
    if payload is None:
        print(" fetch failed - skipping")
        continue

    results = payload.get("results", [])
    if not results:
        print(" empty page")
        continue

    rec = results [0]
    clean = transform_record(rec)
    insert_cultural_site(clean)
    if i == 0:
        print(" rec keys:", list(rec.keys()))
        print(" rec sample:", rec)
    rid = rec.get("id", "no-id")
    fields = rec.get("fields", rec)
    title = fields.get("beschrijving") or fields.get("description") or "(no title)"

    print(f" id={rid} title={title}")


if __name__ == "__main__":
    seen = 0
    for page in page_through(fetch_page, per_page=2, max_pages=3):
        titles = [
            (rec.get("beschrijving") or rec.get("description") or "(no title)")
            for rec in page
        ]
        print(f"page size={len(page)} titles={titles}")
        seen += len(page)
    print("total seen:", seen)

