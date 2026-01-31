import os
import zipfile
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

# Configuração de caminhos na raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJ_ROOT, "data")
ZIP_PATH = os.path.join(DATA_DIR, "consolidado_despesas.zip")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lógica de Startup (Executa ao iniciar)
    if os.path.exists(ZIP_PATH):
        print(f"📦 Extraindo dados consolidados em {DATA_DIR}...")
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
        print("✅ Dados prontos para consulta.")
    else:
        print(f"⚠️ Aviso: ZIP não encontrado em {ZIP_PATH}")

    yield  # Aqui a API funciona

    # Lógica de Shutdown (Executa ao desligar, se necessário)
    print("Stopping API...")


app = FastAPI(
    title="EMPRESA_X - Health Analytics API",
    description="API para processamento e análise de dados de operadoras da ANS.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# --- Lógica de Inicialização (Startup) ---

@app.on_event("startup")
async def startup_event():
    """Garante que os dados estejam descompactados ao iniciar."""
    if os.path.exists(ZIP_PATH):
        print(f"📦 Extraindo dados consolidados em {DATA_DIR}...")
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
        print("✅ Dados prontos para consulta.")
    else:
        print("⚠️ Aviso: consolidado_despesas.zip não encontrado. Rode o ETL primeiro.")

   
# Configuração de CORS (Essencial para o Vue.js conseguir acessar a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, use a URL específica do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Bem-vindo à API de Analytics da EMPRESA_X",
        "status": "online",
        "docs": "/docs"
    }

# Incluindo as rotas que criaremos nas subpastas
# app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)