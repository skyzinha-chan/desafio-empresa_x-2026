# Serve para testarmos se o FastAPI está "enxergando" a nossa estrutura de pastas
# /backend/app/api/routes/__init__.py
import os
import pandas as pd
from fastapi import APIRouter, Query
from typing import Optional, List

router = APIRouter()

# Pega o caminho da pasta onde o projeto está (empresa-x-teste)
# Pega o caminho absoluto da pasta 'backend'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # .../routes
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))

# A pasta 'data' está no mesmo nível da pasta 'backend', então subimos um nível a partir de BACKEND_DIR
PROJ_ROOT = os.path.dirname(BACKEND_DIR)
CSV_PATH = os.path.join(PROJ_ROOT, "data", "consolidado_despesas.csv")


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


@router.get("/despesas", tags=["Analytics"])
async def get_despesas(
    cnpj: Optional[str] = Query(None, description="Filtrar por CNPJ"),
    ano: Optional[int] = Query(None, description="Filtrar por Ano"),
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, le=100, description="Registros por página")
):
    # Log para debug (aparecerá no seu terminal)
    print(f"🔍 Buscando dados em: {CSV_PATH}")

    if not os.path.exists(CSV_PATH):
        return {
            "error": "Dados consolidados não encontrados.",
            "detalhes": f"O sistema buscou em: {CSV_PATH}. Verifique se o arquivo CSV existe nesta pasta."
        }

    # Lendo o CSV (usando sep=';' conforme gerado pelo seu DataProcessor)
    try:
        df = pd.read_csv(CSV_PATH, sep=';', encoding='utf-8-sig', dtype={'CNPJ': str})
        
        # Filtros
        if cnpj:
            df = df[df['CNPJ'] == cnpj]
        if ano:
            df = df[df['ANO'] == ano]

        # Lógica de Paginação
        start = (page - 1) * per_page
        end = start + per_page

        return {
            "total_records": len(df),
            "page": page,
            "per_page": per_page,
            "data": df.iloc[start:end].to_dict(orient="records")
        }
    except Exception as e:
        return {"error": f"Erro interno ao ler processar os dados: {str(e)}"}
# Note que exportamos o router para ser incluído no main.py
