"""Search utilities for Google lookup and browser fallback."""

import json
import os
import urllib.parse
import webbrowser
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None


CONFIG_PATH = Path(__file__).resolve().parent.parent / "google_search_config.json"


def load_google_config() -> tuple[str | None, str | None]:
    """Load Google search API keys from environment or config file."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    cx = os.environ.get("GOOGLE_CX")
    if api_key and cx:
        return api_key, cx

    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            api_key = api_key or data.get("AIzaSyAExp2FQ7AJrtoweW5EDjIHP8gq1weY4MU")
            cx = cx or data.get("GOOGLE_CX")
        except Exception:
            pass

    return api_key, cx


def save_google_config(api_key: str, cx: str) -> None:
    """Save Google search API keys to a local config file."""
    data = {"AIzaSyAExp2FQ7AJrtoweW5EDjIHP8gq1weY4MU": api_key, "GOOGLE_CX": cx}
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def google_custom_search(query: str, api_key: str, cx: str, num: int = 3) -> list[dict]:
    """Search Google using the Custom Search JSON API."""
    if requests is None:
        raise RuntimeError("Please install requests: pip install requests")
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": num,
    }
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    items = data.get("items", [])
    results = []
    for item in items:
        results.append({
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "link": item.get("link", ""),
        })
    return results


def google_search(query: str, api_key: str | None = None, cx: str | None = None, num: int = 3) -> list[dict]:
    """Search Google by API if credentials are available, otherwise open browser search."""
    api_key = api_key or load_google_config()[0]
    cx = cx or load_google_config()[1]

    if api_key and cx:
        return google_custom_search(query, api_key, cx, num=num)

    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}"
    webbrowser.open(url, new=2)
    return []
