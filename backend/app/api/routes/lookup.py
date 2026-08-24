from fastapi import APIRouter, HTTPException, Depends
from app.schemas.lookup import LookupResponse
from app.services.lookup_service import LookupService

router = APIRouter()

# Dependency injection for LookupService
def get_lookup_service() -> LookupService:
    return LookupService()

@router.get("/lookup/{query:path}", response_model=LookupResponse, tags=["Lookup"])
async def perform_lookup(query: str, lookup_service: LookupService = Depends(get_lookup_service)):
    """
    Perform a comprehensive lookup for a domain, IP address, or ASN.
    """
    try:
        result = await lookup_service.lookup(query)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # In a real app we'd log the full exception
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
