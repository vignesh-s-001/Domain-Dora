from app.schemas.lookup import SSLInfo
from typing import Dict, Any
from datetime import datetime

def _parse_x509_name(name_tuple: tuple) -> Dict[str, str]:
    """
    Parses the nested tuple structure of X509 names into a flat dictionary.
    e.g. ((('countryName', 'US'),), (('organizationName', 'Google Trust Services LLC'),))
    """
    result = {}
    for rdn in name_tuple:
        for attr in rdn:
            if len(attr) == 2:
                result[attr[0]] = attr[1]
    return result

def normalize_ssl(raw_cert: Dict[str, Any] | None) -> SSLInfo:
    """
    Normalizes the raw peer certificate dictionary into the SSLInfo schema.
    """
    if not raw_cert:
        return SSLInfo(available=False, status="unavailable or invalid")
        
    # Extract subjects and issuers
    subject = _parse_x509_name(raw_cert.get("subject", ()))
    issuer = _parse_x509_name(raw_cert.get("issuer", ()))
    
    # Dates
    valid_from = None
    valid_to = None
    days_remaining = None
    
    # format: 'Oct 23 08:29:45 2023 GMT'
    date_format = "%b %d %H:%M:%S %Y %Z"
    
    not_before = raw_cert.get("notBefore")
    if not_before:
        try:
            valid_from = datetime.strptime(not_before, date_format)
        except ValueError:
            pass
            
    not_after = raw_cert.get("notAfter")
    if not_after:
        try:
            valid_to = datetime.strptime(not_after, date_format)
            days_remaining = (valid_to - datetime.utcnow()).days
        except ValueError:
            pass
            
    # SAN
    san_list = []
    for san_type, san_val in raw_cert.get("subjectAltName", ()):
        if san_type == "DNS":
            san_list.append(san_val)
            
    serialNumber = raw_cert.get("serialNumber")
    
    return SSLInfo(
        available=True,
        status="valid", # Since we used CERT_REQUIRED, if we get here it's valid
        subject=subject,
        issuer=issuer,
        valid_from=valid_from,
        valid_to=valid_to,
        days_remaining=days_remaining,
        serial_number=serialNumber,
        signature_algorithm=None, # python ssl doesn't expose this easily in getpeercert()
        san=san_list
    )
