import asyncio
from typing import List
import ipaddress

from app.utils.query_detector import detect_query_type
from app.utils.domain import normalize_domain
from app.services.rdap_bootstrap_service import rdap_bootstrap_service
from app.services.rdap_service import rdap_service
from app.services.dns_service import dns_service
from app.services.ssl_service import ssl_service
from app.services.ip_service import ip_service

from app.normalizers.rdap_normalizer import normalize_domain_rdap
from app.normalizers.dns_normalizer import normalize_dns
from app.normalizers.ssl_normalizer import normalize_ssl
from app.normalizers.network_normalizer import normalize_network_rdap

from app.schemas.lookup import LookupResponse, ErrorDetail, NetworkInfo

def extract_unique_ips(dns_result) -> List[str]:
    ips = set()
    if dns_result:
        for record in dns_result.a:
            ips.add(record.get("value"))
        for record in dns_result.aaaa:
            ips.add(record.get("value"))
    return list(ips)

class LookupService:
    async def lookup(self, query: str) -> LookupResponse:
        query_type = detect_query_type(query)

        if query_type == "domain":
            return await self.lookup_domain(query)
        elif query_type == "ip":
            raise NotImplementedError("Standalone IP lookup is not yet implemented (Phase 5 bonus).")
        elif query_type == "asn":
            raise NotImplementedError("ASN lookup is not yet implemented (Phase 5 bonus).")
        
        raise ValueError("Unsupported query type.")

    async def lookup_domain(self, domain: str) -> LookupResponse:
        # 1. Normalize
        domain_parts = normalize_domain(domain)
        errors = []
        
        # 2. Discover RDAP server
        rdap_server = await rdap_bootstrap_service.get_domain_rdap_server(domain_parts.suffix)
        
        # 3. Define parallel tasks
        async def fetch_rdap():
            if not rdap_server:
                errors.append(ErrorDetail(service="rdap", message=f"No authoritative server for TLD: {domain_parts.suffix}"))
                return None
            try:
                raw = await rdap_service.lookup_domain(rdap_server, domain_parts.normalized)
                if not raw:
                    errors.append(ErrorDetail(service="rdap", message="Domain not found in RDAP."))
                return raw
            except Exception as e:
                errors.append(ErrorDetail(service="rdap", message=str(e)))
                return None

        async def fetch_dns():
            try:
                return await dns_service.lookup(domain_parts.normalized)
            except Exception as e:
                errors.append(ErrorDetail(service="dns", message=str(e)))
                return None
                
        async def fetch_ssl():
            try:
                return await ssl_service.lookup(domain_parts.normalized)
            except Exception as e:
                errors.append(ErrorDetail(service="ssl", message=str(e)))
                return None

        # Execute RDAP, DNS, and SSL concurrently
        rdap_raw, dns_raw, ssl_raw = await asyncio.gather(
            fetch_rdap(),
            fetch_dns(),
            fetch_ssl(),
            return_exceptions=False
        )

        # 4. Normalize primary results
        domain_info = normalize_domain_rdap(rdap_raw) if rdap_raw else None
        dns_info = normalize_dns(dns_raw) if dns_raw else None
        ssl_info = normalize_ssl(ssl_raw) if ssl_raw else None
        
        # 5. Network lookup (extract IPs from DNS)
        network_info = None
        if dns_info:
            unique_ips = extract_unique_ips(dns_info)
            if unique_ips:
                network_info = NetworkInfo(resolved_ips=unique_ips)
                
                # Fetch IP RDAP for all resolved IPs concurrently
                async def fetch_ip_rdap(ip_addr):
                    server = await rdap_bootstrap_service.get_ip_rdap_server(ip_addr)
                    if server:
                        return await ip_service.lookup(server, ip_addr)
                    return None
                    
                ip_tasks = [fetch_ip_rdap(ip) for ip in unique_ips]
                ip_results_raw = await asyncio.gather(*ip_tasks, return_exceptions=True)
                
                details = {}
                for ip, ip_raw in zip(unique_ips, ip_results_raw):
                    if isinstance(ip_raw, Exception) or ip_raw is None:
                        continue
                    norm = normalize_network_rdap(ip_raw)
                    if norm:
                        details[ip] = norm
                
                network_info.details = details

        return LookupResponse(
            query=domain_parts.input,
            type="domain",
            domain=domain_info,
            dns=dns_info,
            ssl=ssl_info,
            network=network_info,
            errors=errors
        )
