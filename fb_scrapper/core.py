from typing import List, Optional, Dict
from .utils import NetworkHandler, re
from .utils import HTMLParser as HTMLAnalyzer


class PageDetails:
    def __init__(self, page_url: str):
        self.page_url = self.format_url(page_url)
        self.network = NetworkHandler()
        self.general_data: Dict[str, Optional[str]] = {}
        self.profile_data: Dict[str, Optional[str]] = {}

    @staticmethod
    def format_url(input_url: str) -> str:
        base = "https://www.facebook.com/"
        if not input_url.startswith(base):
            if input_url.startswith("/"):
                input_url = input_url[1:]
            return base + input_url
        return input_url

    def gather_data(self) -> Optional[Dict[str, Optional[str]]]:
        html = self.network.get_html(self.page_url)

        general_json = self.network.extract_json(html, "username_for_profile")
        self.general_data = self.parse_general_data(general_json)

        profile_json = self.network.extract_json(html, "profile_tile_items")
        self.profile_data = self.parse_profile_data(profile_json)

        meta_data = self.parse_meta_data(html)

        if self.general_data and self.profile_data:
            combined = {**self.general_data, **meta_data, **self.profile_data}
            return combined
        elif self.general_data:
            return self.general_data
        elif self.profile_data:
            return self.profile_data
        else:
            return None

    def parse_general_data(self, json_data: dict) -> Dict[str, Optional[str]]:
        data = {
            "name": None,
            "url": None,
            "image": None,
            "likes": None,
            "followers": None,
            "id": None,
            "is_business": None
        }

        try:
            requires = json_data.get("require", [])
            if not requires:
                raise ValueError("No 'require' key found.")
            requires = requires[0][3][0].get("__bbox", {}).get("require", [])

            for require in requires:
                if "RelayPrefetchedStreamCache" in require:
                    result = require[3][1].get("__bbox", {}).get("result", {})
                    user = result.get("data", {}).get("user", {}).get("profile_header_renderer", {}).get("user", {})

                    data["name"] = user.get("name")
                    data["url"] = user.get("url")
                    data["id"] = user.get("delegate_page", {}).get("id")
                    data["is_business"] = user.get("delegate_page", {}).get("is_business_page_active")
                    data["image"] = (
                        user.get("profilePicLarge", {}).get("uri")
                        or user.get("profilePicMedium", {}).get("uri")
                        or user.get("profilePicSmall", {}).get("uri")
                    )

                    social_context = user.get("profile_social_context", {}).get("content", [])
                    for content in social_context:
                        uri = content.get("uri", "")
                        text = content.get("text", {}).get("text")
                        if "friends_likes" in uri and not data["likes"]:
                            data["likes"] = text
                        elif "followers" in uri and not data["followers"]:
                            data["followers"] = text
                        if data["likes"] and data["followers"]:
                            break
            return data
        except (IndexError, KeyError, TypeError, ValueError) as e:
            print(f"Error parsing general data: {e}")
            return data

    def parse_profile_data(self, json_data: dict) -> Dict[str, Optional[str]]:
        fields = {
            "INTRO_CARD_INFLUENCER_CATEGORY": "category",
            "INTRO_CARD_ADDRESS": "address",
            "INTRO_CARD_PROFILE_PHONE": "phone",
            "INTRO_CARD_PROFILE_EMAIL": "email",
            "INTRO_CARD_WEBSITE": "website",
            "INTRO_CARD_BUSINESS_HOURS": "hours",
            "INTRO_CARD_BUSINESS_PRICE": "price",
            "INTRO_CARD_RATING": "rating",
            "INTRO_CARD_BUSINESS_SERVICES": "services",
            "INTRO_CARD_OTHER_ACCOUNT": "social_accounts",
        }

        profile = {value: None for value in fields.values()}

        try:
            requires = json_data.get("require", [])
            if not requires:
                raise ValueError("No 'require' key found.")
            requires = requires[0][3][0].get("__bbox", {}).get("require", [])

            for require in requires:
                if "RelayPrefetchedStreamCache" in require:
                    result = require[3][1].get("__bbox", {}).get("result", {})
                    sections = result.get("data", {}).get("profile_tile_sections", {}).get("edges", [])

                    for section in sections:
                        nodes = section.get("node", {}).get("profile_tile_views", {}).get("nodes", [])
                        for node in nodes:
                            renderer = node.get("view_style_renderer")
                            if not renderer:
                                continue
                            items = renderer.get("view", {}).get("profile_tile_items", {}).get("nodes", [])
                            for item in items:
                                context = item.get("node", {}).get("timeline_context_item", {})
                                item_type = context.get("timeline_context_list_item_type")
                                if item_type in fields:
                                    text = context.get("renderer", {}).get("context_item", {}).get("title", {}).get("text")
                                    if text:
                                        profile[fields[item_type]] = text
            return profile
        except (IndexError, KeyError, TypeError, ValueError) as e:
            print(f"Error parsing profile data: {e}")
            return profile

    def parse_meta_data(self, html: HTMLAnalyzer) -> Dict[str, Optional[str]]:
        meta = {
            "likes_count": None,
            "talking_count": None,
            "were_here_count": None,
        }

        try:
            description = html.css_first("meta[name=description]").attrs.get("content") if html.css_first("meta[name=description]") else None
            if not description:
                return meta

            like_match = re.search(r"(?P<likes>[\d,]+)\s+likes", description)
            meta["likes_count"] = like_match.group("likes") if like_match else None

            talking_match = re.search(r"(?P<talking>[\d,]+)\s+talking about this", description)
            meta["talking_count"] = talking_match.group("talking") if talking_match else None

            were_match = re.search(r"(?P<were>[\d,]+)\s+were here", description)
            meta["were_here_count"] = were_match.group("were") if were_match else None

            return meta
        except Exception as e:
            print(f"Error parsing meta data: {e}")
            return meta

    @classmethod
    def retrieve(cls, url: str) -> Optional[Dict[str, Optional[str]]]:
        scraper = cls(url)
        return scraper.gather_data()