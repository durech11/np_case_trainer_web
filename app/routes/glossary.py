from fastapi import APIRouter, HTTPException
from app.services.glossary import get_definition

router = APIRouter(prefix="/api/glossary", tags=["glossary"])

@router.get("/{term}")
def fetch_definition(term: str):
    result = get_definition(term)
    if not result:
        raise HTTPException(status_code=404, detail="Definition not found")
    return result