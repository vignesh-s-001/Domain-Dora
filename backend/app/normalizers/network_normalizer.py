from typing import Dict, Any
import ipaddress

def _extract_country(raw_data: dict) -> str | None:
    return raw_data.get("country")

def _extract_asn(raw_data: dict) -> str | None:
    # Some RDAP responses might embed ASN in entities or specific objects.
    # In some IP RDAP (like RIPE/ARIN), the ASN might not be directly at the root, 
    # but some provide a "parentHandle" or "handle" representing the netblock, 
    # and ASN is fetched via an autnum lookup.
    # We will try to extract simple fields if available.
    pass

def normalize_network_rdap(raw_data: dict | None) -> Dict[str, Any] | None:
    """
    Normalizes a single IP RDAP response to extract network/org information.
    """
    if not raw_data:
        return None
        
    start_addr = raw_data.get("startAddress")
    end_addr = raw_data.get("endAddress")
    
    cidr = None
    if start_addr and end_addr:
        try:
            # We can convert start/end to a CIDR range roughly, or just report them
            cidr = f"{start_addr} - {end_addr}"
        except Exception:
            pass

    org = None
    country = _extract_country(raw_data)
    
    # Try to extract Organization Name and Country from entities
    entities = raw_data.get("entities", [])
    for entity in entities:
        roles = entity.get("roles", [])
        if "registrant" in roles or "administrative" in roles or "abuse" in roles:
            vcard_array = entity.get("vcardArray", [])
            if len(vcard_array) > 1:
                properties = vcard_array[1]
                for prop in properties:
                    if prop[0] == "fn" and not org:
                        org = prop[3]
                    elif prop[0] == "org" and not org:
                        org = prop[3]
                    elif prop[0] == "adr" and not country:
                        # vcard adr format: ["adr", {}, "text", ["", "", "Street", "City", "State", "Zip", "Country"]]
                        try:
                            adr_parts = prop[3]
                            if len(adr_parts) > 6 and adr_parts[6]:
                                country = adr_parts[6]
                        except Exception:
                            pass
    
    return {
        "cidr": cidr,
        "country": country,
        "organization": org,
        "name": raw_data.get("name")
    }
