import asyncio
import dns.asyncresolver
import dns.exception
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DNSService:
    def __init__(self, timeout: int = 5):
        self.resolver = dns.asyncresolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout
        
        # We want to query these types
        self.record_types = ["A", "AAAA", "MX", "TXT", "NS", "CNAME", "SOA", "CAA"]

    async def _resolve_record(self, domain: str, record_type: str) -> list:
        try:
            answers = await self.resolver.resolve(domain, record_type)
            results = []
            for rdata in answers:
                results.append({
                    "value": rdata.to_text(),
                    "ttl": answers.rrset.ttl if answers.rrset else None
                })
            return results
        except dns.resolver.NoAnswer:
            # Expected if the record type doesn't exist for the domain
            return []
        except dns.resolver.NXDOMAIN:
            # Domain doesn't exist at all
            return []
        except dns.exception.Timeout:
            logger.warning(f"DNS timeout querying {record_type} for {domain}")
            return []
        except Exception as e:
            logger.warning(f"DNS error querying {record_type} for {domain}: {e}")
            return []

    async def lookup(self, domain: str) -> Dict[str, list]:
        """
        Query all DNS record types for a domain concurrently.
        """
        tasks = [self._resolve_record(domain, record_type) for record_type in self.record_types]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        output = {}
        for r_type, result in zip(self.record_types, results):
            if isinstance(result, Exception):
                output[r_type.lower()] = []
            else:
                output[r_type.lower()] = result
                
        return output

dns_service = DNSService()
