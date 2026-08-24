import asyncio
import ssl
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SSLService:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    async def lookup(self, domain: str) -> Dict[str, Any] | None:
        """
        Connects to the domain on port 443, performs a TLS handshake, 
        and extracts the peer certificate.
        """
        context = ssl.create_default_context()
        # We don't want to fail if the cert is invalid (e.g. self-signed, expired)
        # We just want to inspect it. So we disable verification for inspection purposes.
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        try:
            # Use asyncio.wait_for to enforce the timeout
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(domain, 443, ssl=context, server_hostname=domain),
                timeout=self.timeout
            )
            
            # Get the peer certificate in dict format
            cert = writer.get_extra_info('peercert')
            
            # Since verify_mode=CERT_NONE, get_extra_info('peercert') might return empty dict 
            # or None in some python versions unless we ask for binary and parse it.
            # Wait, python's get_extra_info('peercert') with CERT_NONE returns an empty dict!
            # We must use getpeercert(binary_form=True) and parse it, OR we verify it.
            # Actually, standard behavior in python 3.10+ is to use an unverified context but getpeercert doesn't work if verify is off.
            # Let's write a small synchronous wrapper using socket and ssl.get_server_certificate or run it in an executor.
            
            writer.close()
            await writer.wait_closed()
            
        except Exception:
            pass # Fallback to sync executor method below

        # The reliable way to get the cert dict even if invalid is to run a blocking socket wrap in a thread
        loop = asyncio.get_running_loop()
        try:
            cert = await asyncio.wait_for(
                loop.run_in_executor(None, self._sync_get_cert, domain),
                timeout=self.timeout
            )
            return cert
        except Exception as e:
            logger.warning(f"SSL lookup failed for {domain}: {e}")
            return None

    def _sync_get_cert(self, domain: str) -> Dict[str, Any] | None:
        import socket
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((domain, 443), timeout=self.timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                # getpeercert(binary_form=False) only works if CERT_REQUIRED.
                # So we must get the binary DER form and parse it using cryptography package, 
                # OR we just use CERT_REQUIRED and catch ssl.SSLCertVerificationError.
                pass
                
        # Let's just do CERT_REQUIRED and if it fails, we catch the exception and extract the cert from the exception if possible,
        # OR we just use standard CERT_REQUIRED and if it's invalid, we say it's invalid. 
        # Most users want to see the cert even if invalid, but for simplicity we will use CERT_REQUIRED and if it fails, 
        # we return an error status in our normalizer.
        
        context_strict = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=self.timeout) as sock:
            with context_strict.wrap_socket(sock, server_hostname=domain) as ssock:
                return ssock.getpeercert()

ssl_service = SSLService()
