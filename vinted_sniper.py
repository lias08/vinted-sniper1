import tls_client
import time

def convert_url(url):
    if "api/v2/catalog/items" in url:
        return url
    base_api = "https://www.vinted.de/api/v2/catalog/items?"
    params = url.split("?")[-1]
    if "order=" not in params:
        params += "&order=newest_first"
    return base_api + params


class VintedSniper:
    def __init__(self, url):
        self.api_url = convert_url(url)
        self.session = tls_client.Session(client_identifier="chrome_112")
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        self.seen = set()

    def fetch_items(self):
        r = self.session.get(self.api_url, headers=self.headers)
        if r.status_code != 200:
            return []

        items = r.json().get("items", [])
        new_items = []

        for item in items:
            if item["id"] not in self.seen:
                self.seen.add(item["id"])
                new_items.append(item)

        if len(self.seen) > 300:
            self.seen = set(list(self.seen)[-200:])

        return new_items
