import tldextract
from pydantic import BaseModel
from urllib.parse import urlparse

class DomainParts(BaseModel):
    input: str
    normalized: str
    target_host: str
    domain: str
    suffix: str
    subdomain: str

def normalize_domain(domain_input: str) -> DomainParts:
    """
    Normalizes a domain input. Removes protocol, paths, etc., and extracts TLD parts.
    - normalized: registered domain (e.g. mekark.com) - used for RDAP/WHOIS
    - target_host: full hostname (e.g. manufacturing.mekark.com) - used for DNS, SSL, Tech
    """
    original_input = domain_input.strip().lower()
    
    # Handle if user passed a URL instead of just domain
    if "://" in original_input:
        parsed = urlparse(original_input)
        host = parsed.hostname or ""
    else:
        # urlparse might not parse correctly without scheme
        if "/" in original_input:
            parsed = urlparse(f"http://{original_input}")
            host = parsed.hostname or ""
        else:
            host = original_input

    # Remove trailing dots
    host = host.rstrip(".")
    
    # Extract parts using tldextract
    extracted = tldextract.extract(host)
    
    if not extracted.suffix:
        raise ValueError("Invalid domain: Missing valid public suffix")
    if not extracted.domain:
        raise ValueError("Invalid domain: Missing registrable domain name")
        
    normalized = extracted.registered_domain
    target_host = host if host else normalized
    
    return DomainParts(
        input=original_input,
        normalized=normalized,
        target_host=target_host,
        domain=extracted.domain,
        suffix=extracted.suffix,
        subdomain=extracted.subdomain
    )

