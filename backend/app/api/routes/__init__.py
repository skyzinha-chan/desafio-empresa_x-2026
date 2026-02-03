# backend/app/api/routes/__init__.py

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from psycopg2.extras import RealDictCursor
from app.db.connection import get_db_connection

router = APIRouter()

# Constante para o CNPJ da Operadora "Unknown/Dummy"
CNPJ_DUMMY = "00000000000000"

# --- ROTA DE SAÚDE DA API ---
@router.get("/health", tags=["System"])
async def health_check():
    """Verifica se a API está online."""
    conn = get_db_connection()
    status = "connected" if conn else "error"
    if conn:
        conn.close()
    return {"status": "healthy", "database": status}

# --- ROTA 1: Listar Operadoras (Busca + Paginação + Filtros + Ordenação) ---


@router.get("/operadoras", tags=["Operadoras"], status_code=200)
async def listar_operadoras(
    search: Optional[str] = Query(
        None, description="Buscar por Razão Social ou CNPJ"),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    filter_type: str = Query(
        'todas', description="todas, com_dados, sem_dados, desconhecidas"),
    sort_uf: Optional[str] = Query(None, description="asc, desc")
):
    """
    Lista operadoras com suporte a busca, paginação, filtros e ordenação.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(
            status_code=500, detail="Erro de conexão com o banco.")

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        offset = (page - 1) * limit

        # 1. Construção Dinâmica do WHERE
        conditions = ["1=1"]  # Base verdadeira para concatenar ANDs
        params = []

        # --- Filtro de Texto (Busca) - POSTGRES (ILIKE)  ---
        if search:
            conditions.append("(razao_social ILIKE %s OR cnpj ILIKE %s)")
            term = f"%{search}%"
            params.extend([term, term])
            
        # --- LÓGICA DE FILTROS  ---
        if filter_type == 'com_dados':
            # Retorna quem TEM registro E NÃO É a dummy
            conditions.append(
                f"cnpj IN (SELECT DISTINCT cnpj_operadora FROM despesas) AND cnpj != '{CNPJ_DUMMY}'")
            
        elif filter_type == 'sem_dados':
            # Retorna quem NÃO TEM registro E NÃO É a dummy
            conditions.append(
                f"cnpj NOT IN (SELECT DISTINCT cnpj_operadora FROM despesas) AND cnpj != '{CNPJ_DUMMY}'")
            
        elif filter_type == 'desconhecidas':
            # [NOVO] Retorna APENAS a operadora dummy (que segura as despesas órfãs)
            conditions.append(f"cnpj = '{CNPJ_DUMMY}'")

        else:  # 'todas'
            # Retorna todas, mas ESCONDE a dummy para não poluir a lista geral
            conditions.append(f"cnpj != '{CNPJ_DUMMY}'")
            
        where_clause = " WHERE " + " AND ".join(conditions)

        # 2. Contagem Total (Essencial para a paginação funcionar com filtro)
        count_sql = f"SELECT COUNT(*) as total FROM operadoras {where_clause}"
        cursor.execute(count_sql, params)
        total_records = cursor.fetchone()['total']

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
            LIMIT %s OFFSET %s
        """

        # Adiciona params de limite e offset no final da lista
        query_params = params + [limit, offset]

        cursor.execute(sql, query_params)
        operadoras = cursor.fetchall()

        return {
            "data": operadoras,
            "meta": {
                "total": total_records,
                "page": page,
                "limit": limit,
                "total_pages": (total_records + limit - 1) // limit if total_records > 0 else 1
            }
        }
    except Exception as e:
        print(f"Erro ao listar operadoras: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# --- ROTA 2: Detalhes e Histórico da Operadora ---


@router.get("/operadoras/{cnpj}/despesas", tags=["Operadoras"], status_code=200)
async def obter_detalhes_operadora(cnpj: str):
    """
    Retorna detalhes cadastrais e histórico de despesas de uma operadora.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Erro de conexão.")

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 1. Dados Cadastrais (Usando %s)
        cursor.execute("SELECT * FROM operadoras WHERE cnpj = %s", (cnpj,))
        op = cursor.fetchone()

        if not op:
            raise HTTPException(
                status_code=404, detail="Operadora não encontrada")

        # 2. Histórico de Despesas
        if cnpj == CNPJ_DUMMY:
            # --- VISÃO DETALHADA PARA DESCONHECIDAS ---
            # Mostra o 'codigo_origem' (REG_ANS) para sabermos quem são os 15 registros
            cursor.execute("""
                SELECT 
                    ano, 
                    trimestre, 
                    codigo_origem as registro_ans_original, 
                    SUM(valor_despesa) as valor_despesa 
                FROM despesas 
                WHERE cnpj_operadora = %s 
                GROUP BY ano, trimestre, codigo_origem
                ORDER BY ano DESC, trimestre DESC, valor_despesa DESC
            """, (cnpj,))
        else:
            # VISÃO PADRÃO (Agrupada por Trimestre)
            cursor.execute("""
                SELECT 
                    ano, 
                    trimestre, 
                    SUM(valor_despesa) as valor_despesa 
                FROM despesas 
                WHERE cnpj_operadora = %s 
                GROUP BY ano, trimestre
                ORDER BY ano DESC, trimestre DESC
            """, (cnpj,))

        despesas = cursor.fetchall()
        conn.close()

        return {
            "operadora": op,
            "despesas": despesas
        }
    finally:
        conn.close()


# --- ROTA 3: Estatísticas Gerais (Dashboard) ---

@router.get("/estatisticas", tags=["Dashboard"])
async def obter_estatisticas():
    """
    Retorna KPIs lendo da Tabela de Agregados (Data Mart).
    Estratégia: Pré-cálculo (Opção C do teste).
    Vantagem: Performance extrema (lê poucas linhas).
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Erro de conexão.")

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 1. KPIs Globais (Apenas de operadoras válidas)
        # Somamos os totais e tiramos a média das médias trimestrais
        cursor.execute("""
            SELECT 
                SUM(total_despesas) as total_geral,
                AVG(media_trimestral) as media_geral
            FROM despesas_agregadas
            WHERE razao_social != 'OPERADORA DESCONHECIDA / INATIVA'
              AND uf != 'BR'
        """)
        kpis = cursor.fetchone()

        # 2. Top 5 Operadoras (EXCLUI o Dummy para o ranking ser justo)
        cursor.execute("""
            SELECT razao_social, uf, total_despesas as total, desvio_padrao
            FROM despesas_agregadas
            WHERE razao_social != 'OPERADORA DESCONHECIDA / INATIVA'
            ORDER BY total_despesas DESC
            LIMIT 5
        """)
        top_5 = cursor.fetchall()

        # 3. Distribuição por UF (Remove a UF 'BR' ou o nome da Dummy)
        cursor.execute("""
            SELECT uf, SUM(total_despesas) as total
            FROM despesas_agregadas
            WHERE uf != 'BR' 
              AND razao_social != 'OPERADORA DESCONHECIDA / INATIVA'
            GROUP BY uf
            ORDER BY total DESC
            LIMIT 5
        """)
        top_ufs = cursor.fetchall()

        # --- Query 1 (Maior Crescimento % entre 1º e Último Tri) ---
        # 4. Top Crescimento (EXCLUI o Dummy) 
        cursor.execute("""
            WITH limites AS (
                SELECT MIN(ano * 10 + trimestre) as periodo_ini, 
                       MAX(ano * 10 + trimestre) as periodo_fim 
                FROM despesas
            ),
            valores_pontas AS (
                SELECT 
                    d.cnpj_operadora,
                    SUM(CASE WHEN (d.ano * 10 + d.trimestre) = l.periodo_ini THEN d.valor_despesa ELSE 0 END) as vlr_inicial,
                    SUM(CASE WHEN (d.ano * 10 + d.trimestre) = l.periodo_fim THEN d.valor_despesa ELSE 0 END) as vlr_final
                FROM despesas d, limites l
                WHERE d.cnpj_operadora != %s
                GROUP BY d.cnpj_operadora
            )
            SELECT 
                o.razao_social,
                o.uf,
                ROUND(((v.vlr_final - v.vlr_inicial) / NULLIF(v.vlr_inicial, 0)) * 100, 2) as crescimento_pct
            FROM valores_pontas v
            JOIN operadoras o ON v.cnpj_operadora = o.cnpj
            WHERE v.vlr_inicial > 0
            ORDER BY crescimento_pct DESC
            LIMIT 5
        """, (CNPJ_DUMMY,))
        top_crescimento = cursor.fetchall()

        return {
            "kpis": {
                "total_despesas": kpis['total_geral'] or 0,
                "media_trimestral_media": kpis['media_geral'] or 0
            },
            "top_operadoras": top_5,
            "distribuicao_uf": top_ufs,
            "top_crescimento": top_crescimento  
        }
    except Exception as e:
        print(f"Erro estatisticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()