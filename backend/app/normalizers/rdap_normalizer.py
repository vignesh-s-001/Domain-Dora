from typing import Any, List, Optional
from datetime import datetime
from app.schemas.lookup import DomainInfo, RegistrarInfo

def _find_event(events: List[dict], action: str) -> Optional[datetime]:
    if not events:
        return None
    for event in events:
        if event.get("eventAction") == action:
            date_str = event.get("eventDate")
            if date_str:
                # Handle various ISO 8601 formats returned by RDAP
                # e.g., "2023-01-01T00:00:00Z"
                try:
                    # Python 3.11+ supports fromisoformat with Z, otherwise we replace it
                    date_str = date_str.replace("Z", "+00:00")
                    return datetime.fromisoformat(date_str)
                except ValueError:
                    return None
    return None

def normalize_domain_rdap(raw_data: dict) -> DomainInfo:
    """
    Normalizes a raw RDAP domain response into our DomainInfo schema.
    """
    if not raw_data:
        raise ValueError("Cannot normalize empty RDAP data")
        
    name = raw_data.get("ldhName", "")
    
    # Extract entities (registrar, etc.)
    registrar_info = RegistrarInfo()
    entities = raw_data.get("entities", [])
    for entity in entities:
        roles = entity.get("roles", [])
        if "registrar" in roles:
            # VCard array parsing
            vcard_array = entity.get("vcardArray", [])
            if len(vcard_array) > 1:
                properties = vcard_array[1]
                for prop in properties:
                    if prop[0] == "fn":
                        registrar_info.name = prop[3]
                    elif prop[0] == "email":
                        registrar_info.contact_email = prop[3]
                    elif prop[0] == "tel":
                        registrar_info.contact_phone = prop[3]
            
            # Extract public IDs like IANA ID
            public_ids = entity.get("publicIds", [])
            for pid in public_ids:
                if pid.get("type") == "IANA Registrar ID":
                    registrar_info.iana_id = str(pid.get("identifier"))
            break
            
    # Extract dates
    events = raw_data.get("events", [])
    created_at = _find_event(events, "registration")
    updated_at = _find_event(events, "last changed")
    expires_at = _find_event(events, "expiration")
    
    # Extract statuses
    statuses = raw_data.get("status", [])
    
    # Extract nameservers
    nameservers = []
    ns_objs = raw_data.get("nameservers", [])
    for ns in ns_objs:
        ns_name = ns.get("ldhName")
        if ns_name:
            nameservers.append(ns_name.lower())
            
    # Extract DNSSEC
    dnssec = None
    secure_dns = raw_data.get("secureDNS")
    if secure_dns:
        delegation_signed = secure_dns.get("delegationSigned")
        if delegation_signed is True:
            dnssec = "signedDelegation"
        elif delegation_signed is False:
            dnssec = "unsigned"
            
    return DomainInfo(
        name=name.lower(),
        registrar=registrar_info,
        created_at=created_at,
        updated_at=updated_at,
        expires_at=expires_at,
        statuses=statuses,
        nameservers=nameservers,
        dnssec=dnssec
    )
