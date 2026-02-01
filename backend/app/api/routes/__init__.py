# backend/app/api/routes/__init__.py
from fastapi import APIRouter, HTTPException, Query
import sqlite3
import os
from typing import Optional, List

router = APIRouter()

# --- CONFIGURAÇÃO DE CAMINHOS ---
# backend/app/api/routes/ -> backend/app/api/ -> backend/app/ -> backend/ -> data/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(
    CURRENT_DIR, "../../../../data/empresa_x.db"))


def get_db_connection():
    """Abre conexão com o SQLite e retorna linhas como dicionários."""
    if not os.path.exists(DB_PATH):
        raise HTTPException(
            status_code=500,
            detail="Banco de dados não encontrado. Certifique-se de ter rodado o ETL (Step 3)."
        )
    conn = sqlite3.connect(DB_PATH)
    # Permite acessar colunas pelo nome (row['nome'])
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/health", tags=["System"])
async def health_check():
    """Verifica se a API está online."""
    return {"status": "healthy", "database": "connected" if os.path.exists(DB_PATH) else "missing"}

# --- ROTA 1: Listar Operadoras (Busca + Paginação + Filtros + Ordenação) ---


@router.get("/operadoras", tags=["Operadoras"])
async def listar_operadoras(
    search: Optional[str] = Query(
        None, description="Buscar por Razão Social ou CNPJ"),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    filter_type: str = Query(
        'todas', description="todas, com_dados, sem_dados"),
    sort_uf: Optional[str] = Query(None, description="asc, desc")
):
    conn = get_db_connection()
    cursor = conn.cursor()

    offset = (page - 1) * limit

    # 1. Construção Dinâmica do WHERE
    conditions = []
    params = []

    # Filtro de Texto (Busca)
    if search:
        conditions.append("(razao_social LIKE ? OR cnpj LIKE ?)")
        term = f"%{search}%"
        params.extend([term, term])

    # Filtro de Abas (Lógica SQL)
    if filter_type == 'com_dados':
        # Retorna apenas quem TEM registro na tabela despesas
        conditions.append(
            "cnpj IN (SELECT DISTINCT cnpj_operadora FROM despesas)")
    elif filter_type == 'sem_dados':
        # Retorna apenas quem NÃO TEM registro
        conditions.append(
            "cnpj NOT IN (SELECT DISTINCT cnpj_operadora FROM despesas)")

    # Junta todas as condições com AND
    where_clause = ""
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)

    # 2. Contagem Total (Essencial para a paginação funcionar com filtro)
    count_sql = f"SELECT COUNT(*) FROM operadoras {where_clause}"
    cursor.execute(count_sql, params)
    total_records = cursor.fetchone()[0]

    # 3. Definição da Ordenação (ORDER BY)
    order_clause = "ORDER BY razao_social ASC"  # Padrão

    if sort_uf == 'asc':
        order_clause = "ORDER BY uf ASC, razao_social ASC"
    elif sort_uf == 'desc':
        order_clause = "ORDER BY uf DESC, razao_social ASC"

    # 4. Busca Final Paginada
    sql = f"""
        SELECT cnpj, razao_social, uf, modalidade 
        FROM operadoras
        {where_clause}
        {order_clause}
        LIMIT ? OFFSET ?
    """

    # Adiciona params de limite e offset no final da lista
    query_params = params + [limit, offset]

    cursor.execute(sql, query_params)
    operadoras = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "data": operadoras,
        "meta": {
            "total": total_records,
            "page": page,
            "limit": limit,
            "total_pages": (total_records + limit - 1) // limit if total_records > 0 else 1
        }
    }

# --- ROTA 2: Detalhes e Histórico da Operadora ---


@router.get("/operadoras/{cnpj}/despesas", tags=["Operadoras"])
async def obter_detalhes_operadora(cnpj: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Dados Cadastrais
    op = cursor.execute(
        "SELECT * FROM operadoras WHERE cnpj = ?", (cnpj,)).fetchone()
    if not op:
        conn.close()
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    # 2. Histórico de Despesas
    cursor.execute("""
        SELECT ano, trimestre, valor_despesa 
        FROM despesas 
        WHERE cnpj_operadora = ? 
        ORDER BY ano DESC, trimestre DESC
    """, (cnpj,))

    despesas = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {
        "operadora": dict(op),
        "despesas": despesas
    }

# --- ROTA 3: Estatísticas Gerais (Dashboard) ---


@router.get("/estatisticas", tags=["Dashboard"])
async def obter_estatisticas():
    """
    Retorna KPIs gerais para o Dashboard (Item 4.2 do desafio).
    Trade-off: Calculado em tempo real (Query Direta). Para volumes maiores, usaríamos cache.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # KPI 1: Total de Despesas no período
        cursor.execute("SELECT SUM(valor_despesa) FROM despesas")
        total_geral = cursor.fetchone()[0] or 0

        # KPI 2: Média por Trimestre
        cursor.execute("SELECT AVG(valor_despesa) FROM despesas")
        media_geral = cursor.fetchone()[0] or 0

        # KPI 3: Top 5 Operadoras com maiores despesas
        cursor.execute("""
            SELECT o.razao_social, o.uf, SUM(d.valor_despesa) as total
            FROM despesas d
            JOIN operadoras o ON d.cnpj_operadora = o.cnpj
            GROUP BY o.cnpj
            ORDER BY total DESC
            LIMIT 5
        """)
        top_5 = [dict(row) for row in cursor.fetchall()]

        # KPI 4: Distribuição por UF (Top 5 Estados)
        cursor.execute("""
            SELECT o.uf, SUM(d.valor_despesa) as total
            FROM despesas d
            JOIN operadoras o ON d.cnpj_operadora = o.cnpj
            GROUP BY o.uf
            ORDER BY total DESC
            LIMIT 5
        """)
        top_ufs = [dict(row) for row in cursor.fetchall()]

        return {
            "kpis": {
                "total_despesas": total_geral,
                "media_por_lancamento": media_geral
            },
            "top_operadoras": top_5,
            "distribuicao_uf": top_ufs
        }
    finally:
        conn.close()
