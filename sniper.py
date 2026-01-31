import tls_client
import time

class VintedSniper:
    def __init__(self, url):
        self.api_url = self.convert_url(url)
        self.session = tls_client.Session(client_identifier="chrome_112")
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        self.seen = set()

    def convert_url(self, url):
        if "api/v2/catalog/items" in url:
            return url
        base = "https://www.vinted.de/api/v2/catalog/items?"
        params = url.split("?")[-1]
        if "order=" not in params:
            params += "&order=newest_first"
        return base + params

    def fetch_items(self):
        try:
            r = self.session.get(self.api_url, headers=self.headers)
            if r.status_code != 200:
                return []

            items = r.json().get("items", [])
            new = []

            for i in items:
                if i["id"] not in self.seen:
                    self.seen.add(i["id"])
                    new.append(i)

            if len(self.seen) > 500:
                self.seen = set(list(self.seen)[-200:])

            return new
        except:
            return []

    # ===== Hilfsfunktionen =====

    def format_price(self, item):
        p = item.get("price") or item.get("total_item_price")
        if isinstance(p, dict):
            return float(p.get("amount", 0))
        return float(p or 0)

    def calc_total_price(self, base_price):
        # grobe Vinted Gebühren
        return round(base_price + 0.70 + base_price * 0.05 + 3.99, 2)

    def get_image(self, item):
        photos = item.get("photos", [])
        if photos:
            return photos[0]["url"].replace("/medium/", "/full/")
        return None

    def get_uploaded_time(self, item):
        ts = item.get("created_at_ts")
        if not ts:
            return "Unbekannt"
        diff = int(time.time() - ts)
        if diff < 60:
            return "gerade eben"
        if diff < 3600:
            return f"vor {diff//60} Min"
        return f"vor {diff//3600} Std"
