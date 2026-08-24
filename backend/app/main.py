from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import lookup

app = FastAPI(
    title="Domain Intelligence Platform API",
    description="API for comprehensive domain, IP, and ASN intelligence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lookup.router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Domain Intelligence Platform is running"}
