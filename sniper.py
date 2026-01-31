import tls_client
import time

class VintedSniper:
    def __init__(self, api_url):
        self.api_url = api_url
        self.session = tls_client.Session(
            client_identifier="chrome_112"
        )
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        self.seen_ids = set()

        # Cookie holen
        try:
            self.session.get("https://www.vinted.de", headers=self.headers)
        except:
            pass

    def fetch_items(self):
        try:
            r = self.session.get(self.api_url, headers=self.headers)
            if r.status_code != 200:
                return []

            data = r.json()
            items = data.get("items", [])
            new_items = []

            for item in items:
                item_id = item.get("id")
                if item_id and item_id not in self.seen_ids:
                    self.seen_ids.add(item_id)
                    new_items.append(item)

            return new_items

        except Exception as e:
            print("❌ Fetch Fehler:", e)
            return []
