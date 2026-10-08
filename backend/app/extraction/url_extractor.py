import re
from typing import List

class URLExtractor:
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        if not text:
            return []
        
        # Regex to find URLs
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        return url_pattern.findall(text)

    @staticmethod
    def get_domain(url: str) -> str:
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain
        except Exception:
            return ""
