from app.schemas.lookup import DNSLookupResult
from typing import Dict, Any, List

def normalize_dns(raw_dns: Dict[str, List[Dict[str, Any]]]) -> DNSLookupResult:
    """
    Normalizes the raw DNS results dictionary into the structured DNSLookupResult model.
    """
    # Helper to just safely extract the list or empty list if None/Exception
    def get_list(key: str) -> list:
        val = raw_dns.get(key, [])
        return val if isinstance(val, list) else []

    soa_records = get_list("soa")
    soa = soa_records[0] if soa_records else None
    
    # We clean up some specific TXT records (removing surrounding quotes)
    txt_records = []
    for txt in get_list("txt"):
        val = txt.get("value", "")
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        txt_records.append({
            "value": val,
            "ttl": txt.get("ttl")
        })

    return DNSLookupResult(
        a=get_list("a"),
        aaaa=get_list("aaaa"),
        mx=get_list("mx"),
        txt=txt_records,
        ns=get_list("ns"),
        cname=get_list("cname"),
        soa=soa,
        caa=get_list("caa")
    )
