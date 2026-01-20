
import logging
import re
import os

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

        # 1. BrightData Dynamic Generation
        if args.brightdata_proxy and args.countries:
            try:
                base_proxy = args.brightdata_proxy.strip()
                countries = [c.strip().lower() for c in args.countries.split(',') if c.strip()]
                
                # Regex to capture parts: (scheme://)(user)(:pass@host:port)
                match = re.match(r"(https?://)([^:]+)(:.+)", base_proxy)
                
                if match and countries:
                    scheme = match.group(1)
                    user = match.group(2)
                    rest = match.group(3)
                    
                    generated_proxies = []
                    for country in countries:
                        # BrightData format: user-country-code
                        new_user = f"{user}-country-{country}"
                        new_proxy = f"{scheme}{new_user}{rest}"
                        generated_proxies.append(new_proxy)
                    
                    if generated_proxies:
                        logger.info(f"Generated {len(generated_proxies)} BrightData proxies for countries: {', '.join(countries)}")
                        return generated_proxies
                else:
                     logger.error("Invalid BrightData proxy format. Use http://user:pass@host:port")
            except Exception as e:
                 logger.error(f"Failed to generate BrightData proxies: {e}")

        # 2. Return default (Direct) if no proxies generated
        if proxies == [None]:
            logger.info("No BrightData proxies configured. Using direct connection.")
            
        return proxies

    def get_source_label(self, proxy, args):
        """
        Returns a human-readable label for the proxy source.
        """
        if not proxy:
            return "Direct"
            
        if args.brightdata_proxy and args.countries:
             c_match = re.search(r'-country-([a-z]{2})', proxy)
             if c_match:
                 return f"BrightData ({c_match.group(1).upper()})"
        
        return proxy
