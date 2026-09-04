import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class IPService:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def lookup(self, rdap_server: str, ip: str) -> Dict[str, Any] | None:
        """
        Query the authoritative RDAP server for IP information.
        """
        if not rdap_server.endswith("/"):
            rdap_server += "/"
            
        url = f"{rdap_server}ip/{ip}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code == 404:
                    logger.info(f"IP {ip} not found in RDAP")
                    return None
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning(f"RDAP IP lookup failed for {ip}: {e}")
            return None

ip_service = IPService()
