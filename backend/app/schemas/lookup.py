from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict
from datetime import datetime

class RegistrarInfo(BaseModel):
    name: Optional[str] = None
    iana_id: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class DomainInfo(BaseModel):
    name: str
    registrar: Optional[RegistrarInfo] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    statuses: List[str] = Field(default_factory=list)
    nameservers: List[str] = Field(default_factory=list)
    dnssec: Optional[str] = None

class DNSLookupResult(BaseModel):
    a: List[dict] = Field(default_factory=list)
    aaaa: List[dict] = Field(default_factory=list)
    mx: List[dict] = Field(default_factory=list)
    txt: List[dict] = Field(default_factory=list)
    ns: List[dict] = Field(default_factory=list)
    cname: List[dict] = Field(default_factory=list)
    soa: Optional[dict] = None
    caa: List[dict] = Field(default_factory=list)

class SSLInfo(BaseModel):
    available: bool = False
    status: Optional[str] = None
    subject: dict = Field(default_factory=dict)
    issuer: dict = Field(default_factory=dict)
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    days_remaining: Optional[int] = None
    serial_number: Optional[str] = None
    signature_algorithm: Optional[str] = None
    san: List[str] = Field(default_factory=list)

class NetworkInfo(BaseModel):
    resolved_ips: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)
    
class ErrorDetail(BaseModel):
    service: str
    message: str

class TechnologyDetection(BaseModel):
    name: str
    category: str
    status: str # "confirmed", "high confidence", "possible", "no evidence"
    confidence: float
    evidence: List[str] = Field(default_factory=list)

class TechnologyInfo(BaseModel):
    frontend: List[TechnologyDetection] = Field(default_factory=list)
    packages: List[TechnologyDetection] = Field(default_factory=list)
    backend: List[TechnologyDetection] = Field(default_factory=list)
    infrastructure: List[TechnologyDetection] = Field(default_factory=list)
    cdn: List[TechnologyDetection] = Field(default_factory=list)
    analytics: List[TechnologyDetection] = Field(default_factory=list)

class LookupResponse(BaseModel):
    query: str
    type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = False
    
    domain: Optional[DomainInfo] = None
    dns: Optional[DNSLookupResult] = None
    ssl: Optional[SSLInfo] = None
    network: Optional[NetworkInfo] = None
    technology: Optional[TechnologyInfo] = None
    
    errors: List[ErrorDetail] = Field(default_factory=list)
