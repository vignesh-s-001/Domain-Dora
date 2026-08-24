import ipaddress
import re

def detect_query_type(query: str) -> str:
    """
    Detects if the query is a domain, IP address, or ASN.
    Returns: "domain", "ip", or "asn"
    """
    query = query.strip()
    
    # Check ASN (e.g. AS15169 or 15169 if we support pure numbers for ASN)
    if re.match(r'^as\d+$', query, re.IGNORECASE):
        return "asn"
    
    # Check IP
    try:
        ip = ipaddress.ip_address(query)
        return "ip"
    except ValueError:
        pass
        
    # Check Domain (basic regex, tldextract will do the rigorous checking later)
    # A domain should have at least one dot, and not end/start with a dot.
    if "." in query and not query.startswith(".") and not query.endswith("."):
        return "domain"
        
    raise ValueError(f"Invalid query format: {query}. Must be a valid domain, IP address, or ASN.")
