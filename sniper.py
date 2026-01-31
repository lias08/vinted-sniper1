import tls_client
import time

class VintedSniper:
    def __init__(self, target_url):
        self.api_url = self.convert_url(target_url)
        self.session = tls_client.Session(client_identifier="chrome_112")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/112.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
        }
        self.seen_items = []

    def convert_url(self, url):
        if "api/v2/catalog/items" in url: return url
        base_api = "https://www.vinted.de/api/v2/catalog/items?"
        params = url.split('?')[-1]
        if params == url: return base_api + "per_page=20&order=newest_first"
        if "order=" not in params: params += "&order=newest_first"
        return base_api + params

    def fetch_cookie(self):
        try:
            self.session.get("https://www.vinted.de", headers=self.headers)
        except: pass

    def fetch_items(self):
        self.fetch_cookie()
        try:
            response = self.session.get(self.api_url, headers=self.headers)
            if response.status_code == 200:
                items = response.json().get("items", [])
                new_items = [i for i in items if i["id"] not in self.seen_items]
                self.seen_items += [i["id"] for i in new_items]
                if len(self.seen_items) > 500:
                    self.seen_items = self.seen_items[-200:]
                return new_items
            else:
                return []
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return []

    def get_clean_status(self, item):
        raw_status = item.get('status_id') or item.get('status') or "Unbekannt"
        mapping = {
            "6": "Neu mit Etikett ✨", "new_with_tags": "Neu mit Etikett ✨",
            "1": "Neu ohne Etikett ✨", "new_without_tags": "Neu ohne Etikett ✨",
            "2": "Sehr gut 👌", "very_good": "Sehr gut 👌",
            "3": "Gut 👍", "good": "Gut 👍",
            "4": "Zufriedenstellend 🆗", "satisfactory": "Zufriedenstellend 🆗"
        }
        return mapping.get(str(raw_status).lower(), str(raw_status))
