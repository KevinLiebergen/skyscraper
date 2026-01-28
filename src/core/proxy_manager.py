import logging
import re
import os
import uuid

logger = logging.getLogger("skyscraper.core.proxy")

class ProxyManager:
    """
    Manages loading and generation of proxies for the scraper.
    """
    def __init__(self):
        pass

    def get_proxies(self, args):
        """
        Determines the list of proxies to use based on the arguments.
        Returns a list of proxy strings (or [None] for direct connection).
        """
        proxies = [None]

        if hasattr(args, 'scraperapi_key') and args.scraperapi_key:
             # Legacy/Fallback if argument re-added, but for now strict SerpApi
             pass
        
        # 2. Return default (Direct) if no proxies generated
        if proxies == [None]:
            logger.info("No proxies configured. Using direct connection.")
            
        return proxies

    def get_source_label(self, proxy, args):
        """
        Returns a human-readable label for the proxy source.
        """
        if not proxy:
            return "Direct"
            
        if  hasattr(args, 'scraperapi_key') and args.scraperapi_key and "scraperapi" in proxy:
            # Extract country code if present
            c_match = re.search(r'country_code=([a-z]{2})', proxy)
            if c_match:
                return f"ScraperAPI ({c_match.group(1).upper()})"
            return "ScraperAPI"
        
        return proxy
