import requests
import time

class VintedSniper:
    def __init__(self, url):
        self.url = url
        self.seen = set()

    def fetch_items(self):
        try:
            r = requests.get(self.url, timeout=10)
            data = r.json()
        except Exception:
            return []

        new_items = []

        for item in data.get("items", []):
            if item["id"] in self.seen:
                continue

            self.seen.add(item["id"])

            new_items.append({
                "id": item["id"],
                "title": item.get("title", "Kein Titel"),
                "brand": item.get("brand", {}).get("title", "Unbekannt"),
                "price": item.get("price", {}).get("amount"),
                "currency": item.get("price", {}).get("currency_code"),
                "condition": item.get("status", "Unbekannt"),
                "image": item.get("photo", {}).get("url"),
                "url": f"https://www.vinted.de/items/{item['id']}",
                "created": item.get("created_at")
            })

        return new_items
