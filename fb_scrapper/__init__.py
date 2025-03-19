from typing import List, Optional, Dict
from .versions import __version__
from .core import PageDetails


class Scraper:

    @staticmethod
    def fetch_page_details(page_url: str) -> Optional[Dict[str, Optional[str]]]:
        return PageDetails.retrieve(page_url)


__all__ = ["Scraper", "PageDetails"]