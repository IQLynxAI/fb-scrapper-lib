from curl_cffi import requests
from selectolax.parser import HTMLParser
import json
import sys
import re


class NetworkHandler:
    def __init__(self):
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        }

    def get_html(self, url: str) -> HTMLParser:
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return HTMLParser(response.text)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            sys.exit(1)

    def extract_json(self, html: HTMLParser, key: str) -> dict:
        try:
            for script in html.css('script[type="application/json"]'):
                script_text = script.text(strip=True)
                if key in script_text:
                    return json.loads(script_text)
            print(f"No data found for key '{key}'.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for key '{key}': {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error for key '{key}': {e}")
            sys.exit(1)