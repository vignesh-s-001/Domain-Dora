import tldextract
from pydantic import BaseModel
from urllib.parse import urlparse

class DomainParts(BaseModel):
    input: str
    normalized: str
    domain: str
    suffix: str
    subdomain: str

def normalize_domain(domain_input: str) -> DomainParts:
    """
    Normalizes a domain input. Removes protocol, paths, etc., and extracts TLD parts.
    """
    original_input = domain_input.strip().lower()
    
    # Handle if user passed a URL instead of just domain
    if "://" in original_input:
        parsed = urlparse(original_input)
        host = parsed.hostname or ""
    else:
        # urlparse might not parse correctly without scheme
        # Let's add a fake scheme just to extract hostname if there are paths
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
    
    # Sometimes we want to include subdomain if it's significant, 
    # but for WHOIS/RDAP, we usually query the registered domain.
    # The requirement: "Determine the registrable domain"
    # Wait, if input is www.example.co.in, normalized should be example.co.in according to the prompt
    
    return DomainParts(
        input=original_input,
        normalized=normalized,
        domain=extracted.domain,
        suffix=extracted.suffix,
        subdomain=extracted.subdomain
    )
