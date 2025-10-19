def transform_record(rec):
    fields = rec.get("fields", rec)
    return {
        "description_nl": fields.get("beschrijving") or "",
        "description_fr": fields.get("description") or "",
        "address_nl": fields.get("adres") or "",
        "address_fr": fields.get("adresse") or "",
        "postal_code": fields.get("code_postal") or "",
        "city_nl": fields.get("plaats") or "",
        "city_fr": fields.get("lieu") or "",
        "google_maps_url": fields.get("google_maps") or "",
        "google_street_view_url": fields.get("google_street_view") or "",
        "longitude": fields.get("coordonnees_geographiques", {}).get("lon"),
        "latitude": fields.get("coordonnees_geographiques", {}).get("lat"),
    }

