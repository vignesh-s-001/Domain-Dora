import httpx
import logging
from typing import Any

logger = logging.getLogger(__name__)

class RDAPService:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def lookup_domain(self, rdap_server: str, domain: str) -> dict | None:
        """
        Query the authoritative RDAP server for domain information.
        Returns the raw JSON dictionary, or None if not found/error.
        """
        # Ensure the rdap_server ends with a slash for proper joining
        if not rdap_server.endswith("/"):
            rdap_server += "/"
            
        url = f"{rdap_server}domain/{domain}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 404:
                    logger.info(f"Domain {domain} not found in RDAP")
                    return None
                    
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"RDAP HTTP error for {domain}: {e}")
            raise Exception(f"RDAP server returned an error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"RDAP Request error for {domain}: {e}")
            raise Exception("Failed to connect to RDAP server")
        except Exception as e:
            logger.error(f"Unexpected error during RDAP lookup for {domain}: {e}")
            raise

rdap_service = RDAPService()
