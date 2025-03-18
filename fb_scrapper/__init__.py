from typing import List, Optional, Dict
from versions import __version__


class FacebookScraper:

    @staticmethod
    def PageInfo(url: str) -> Optional[Dict[str, Optional[str]]]:

        return PageInfo.PageInfo(url)

    @staticmethod
    def PagePostInfo(url: str) -> Optional[List[Dict[str, Optional[str]]]]:

        return PagePostInfo.PagePostInfo(url)


__all__ = ["FacebookPageScraper", "PageInfo", "PagePostInfo"]
