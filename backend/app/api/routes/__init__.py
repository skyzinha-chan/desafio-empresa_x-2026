# Serve para testarmos se o FastAPI está "enxergando" a nossa estrutura de pastas

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Verifica o status da API.
    """
    return {
        "status": "healthy",
        "service": "empresa-x-analytics",
        "version": "1.0.0"
    }
