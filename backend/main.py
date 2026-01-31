import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router

app = FastAPI(
    title="EMPRESA_X - Health Analytics API",
    description="API para processamento e análise de dados de operadoras da ANS.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

   
# Configuração de CORS (Essencial para o Vue.js conseguir acessar a API)
app.add_middleware(
    CORSMiddleware,
    # Em produção, troque "*" por "http://localhost:5173" (porta do Vue)
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "🚀 Bem-vindo à API de Analytics da EMPRESA_X",
        "status": "online",
        "endpoints": {
            "docs": "/docs",
            "operadoras": "/api/operadoras"
        }
    }

# Incluindo as rotas que criaremos nas subpastas
# app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)