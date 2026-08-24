import httpx
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RDAPBootstrapService:
    def __init__(self):
        self._cache = {}
        self._ip_cache = {}
        self._last_fetched = None
        self._cache_ttl = timedelta(hours=24)
        
        self._bootstrap_url_dns = "https://data.iana.org/rdap/dns.json"
        self._bootstrap_url_ipv4 = "https://data.iana.org/rdap/ipv4.json"
        self._bootstrap_url_ipv6 = "https://data.iana.org/rdap/ipv6.json"
        
        self._lock = asyncio.Lock()

    async def _fetch_bootstrap_data(self):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Fetch DNS
                response_dns = await client.get(self._bootstrap_url_dns)
                response_dns.raise_for_status()
                data_dns = response_dns.json()
                
                new_cache = {}
                for service in data_dns.get("services", []):
                    tlds = service[0]
                    urls = service[1]
                    if urls:
                        primary_url = urls[0]
                        for tld in tlds:
                            new_cache[tld] = primary_url
                            
                self._cache = new_cache
                
                # Fetch IPv4 and IPv6
                new_ip_cache = {}
                
                response_ipv4 = await client.get(self._bootstrap_url_ipv4)
                if response_ipv4.status_code == 200:
                    for service in response_ipv4.json().get("services", []):
                        cidrs = service[0]
                        urls = service[1]
                        if urls:
                            for cidr in cidrs:
                                new_ip_cache[cidr] = urls[0]
                                
                response_ipv6 = await client.get(self._bootstrap_url_ipv6)
                if response_ipv6.status_code == 200:
                    for service in response_ipv6.json().get("services", []):
                        cidrs = service[0]
                        urls = service[1]
                        if urls:
                            for cidr in cidrs:
                                new_ip_cache[cidr] = urls[0]

                self._ip_cache = new_ip_cache
                
                self._last_fetched = datetime.utcnow()
                logger.info(f"Loaded RDAP bootstrap data: {len(self._cache)} TLDs, {len(self._ip_cache)} CIDRs")
        except Exception as e:
            logger.error(f"Failed to fetch RDAP bootstrap data: {e}")
            # If we fail but have old cache, keep using it

    async def get_domain_rdap_server(self, suffix: str) -> str | None:
        """
        Get the authoritative RDAP server for a given domain suffix (TLD).
        suffix should be like 'com' or 'co.uk'. 
        RDAP bootstrap usually maps at the top level (e.g. 'uk', 'com').
        """
        async with self._lock:
            if not self._cache or not self._last_fetched or (datetime.utcnow() - self._last_fetched) > self._cache_ttl:
                await self._fetch_bootstrap_data()
        
        # We need to find the TLD from the suffix.
        # For 'co.uk', the RDAP server is often defined at the 'uk' level or 'co.uk' level.
        # Let's try exact match first, then split by dot and try rightmost parts.
        parts = suffix.split(".")
        for i in range(len(parts)):
            candidate = ".".join(parts[i:])
            if candidate in self._cache:
                return self._cache[candidate]
                
        return None

    async def get_ip_rdap_server(self, ip: str) -> str | None:
        """
        Get the authoritative RDAP server for a given IP address.
        """
        import ipaddress
        async with self._lock:
            if not self._ip_cache or not self._last_fetched or (datetime.utcnow() - self._last_fetched) > self._cache_ttl:
                await self._fetch_bootstrap_data()
                
        try:
            ip_obj = ipaddress.ip_address(ip)
            for cidr_str, server in self._ip_cache.items():
                network = ipaddress.ip_network(cidr_str, strict=False)
                if ip_obj in network:
                    return server
        except ValueError:
            pass
            
        return None

rdap_bootstrap_service = RDAPBootstrapService()
