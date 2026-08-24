# Domain Intelligence Platform

A modern WHOIS-like application that provides comprehensive domain, IP, and ASN intelligence.

## Architecture Design

Domain-Dora uses a decoupled, modern architecture designed for speed and concurrent data gathering:

- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, Shadcn UI.
  - Implements a Dual-Theme UI (Premium Dark / Clean Light) with `next-themes`.
  - Runs a robust "Hosting Detection Engine" to interpret raw network IDs into recognizable PaaS/Cloud providers.
- **Backend**: FastAPI, Python 3, Pydantic, `asyncio`, `dnspython`, `httpx`.
  - Uses an Orchestrator pattern (`LookupService`) to spawn concurrent, non-blocking `asyncio` tasks for each intelligence pipeline.
- **Caching**: Redis (Optional)

## How It Works

Domain-Dora acts as an orchestrator that pulls data from multiple layers of the internet infrastructure simultaneously to give a complete picture of a domain or IP address.

1. **The Input & Detection Phase**: The backend `Query Detector` receives the input (cleaning out HTTP/HTTPS and trailing slashes) and determines whether the query is a valid Domain, IPv4/IPv6 address, or ASN.
2. **Concurrent Intelligence Gathering**:
   - **RDAP/WHOIS Investigator**: Connects to IANA to dynamically find the correct authoritative registry (like Verisign), then queries that registry to find ownership, registration, and expiry details.
   - **DNS Investigator**: Asynchronously queries global nameservers for routing records (A, AAAA, MX, TXT, CNAME, NS) using `dnspython`.
   - **SSL/Security Investigator**: Opens a live TLS socket connection over port 443 to inspect the target's certificate cryptography details (Issuer, Subject, Expiry, SANs).
3. **Secondary Network Lookup**: The backend extracts the underlying IP addresses discovered during the DNS phase and immediately triggers a secondary RDAP lookup against the Regional Internet Registries (ARIN, RIPE, APNIC) to find out who owns the physical servers (e.g. AWS, Cloudflare, Google).
4. **Hosting Detection Engine**: The React frontend compiles this intelligence, analyzes CNAMEs, Nameservers, and IP Organizations against known signatures, and visually reports the true Hosting Provider to the user.

## API Design

The backend exposes a single, powerful, RESTful orchestration endpoint:

### `GET /api/v1/lookup/{query:path}`

**Description:** Performs a comprehensive intelligence gather on the provided string.

**Path Parameters:**
- `query` (str): The domain name (e.g., `google.com`), IP address (e.g., `8.8.8.8`), or ASN (e.g., `AS15169`).

**Response Schema (`LookupResponse`):**
```json
{
  "query": "google.com",
  "type": "domain",
  "domain": {
    "name": "google.com",
    "registrar": { "name": "MarkMonitor Inc." },
    "created_at": "1997-09-15T04:00:00Z",
    "expires_at": "2028-09-14T04:00:00Z",
    "nameservers": ["ns1.google.com"],
    "dnssec": "unsigned"
  },
  "dns": {
    "a": [{"value": "142.250.190.46", "ttl": 300}],
    "aaaa": [],
    "mx": [],
    "txt": [],
    "cname": [],
    "ns": []
  },
  "ssl": {
    "available": true,
    "issuer": { "commonName": "GTS CA 1C3" },
    "subject": { "commonName": "*.google.com" },
    "valid_from": "2023-01-01T00:00:00Z",
    "valid_to": "2023-04-01T00:00:00Z"
  },
  "network": {
    "resolved_ips": ["142.250.190.46"],
    "details": {
      "142.250.190.46": {
        "name": "GOOGLE",
        "organization": "Google LLC",
        "cidr": "142.250.190.0/24",
        "country": "US"
      }
    }
  },
  "errors": []
}
```

## Setup

### Backend
```bash
cd backend
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Redis (Optional)
```bash
docker-compose up -d
```
