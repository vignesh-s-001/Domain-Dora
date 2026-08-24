export interface RegistrarInfo {
  name: string | null;
  iana_id: string | null;
}

export interface DomainInfo {
  name: string;
  registrar: RegistrarInfo | null;
  created_at: string | null;
  updated_at: string | null;
  expires_at: string | null;
  statuses: string[];
  nameservers: string[];
  dnssec: string | null;
}

export interface DNSLookupResult {
  a: any[];
  aaaa: any[];
  mx: any[];
  txt: any[];
  ns: any[];
  cname: any[];
  soa: any | null;
  caa: any[];
}

export interface SSLInfo {
  available: boolean;
  status: string | null;
  subject: Record<string, any>;
  issuer: Record<string, any>;
  valid_from: string | null;
  valid_to: string | null;
  days_remaining: number | null;
  serial_number: string | null;
  signature_algorithm: string | null;
  san: string[];
}

export interface NetworkInfo {
  resolved_ips: string[];
}

export interface ErrorDetail {
  service: string;
  message: string;
}

export interface LookupResponse {
  query: string;
  type: string;
  timestamp: string;
  cached: boolean;
  
  domain: DomainInfo | null;
  dns: DNSLookupResult | null;
  ssl: SSLInfo | null;
  network: NetworkInfo | null;
  
  errors: ErrorDetail[];
}
