import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """
    Cria uma conexão com o PostgreSQL usando as variáveis de ambiente do Docker.
    """
    try:
        # Pega a URL do ambiente ou usa um valor default para teste local
        # Formato: postgresql://user:pass@host:5432/db
        db_url = os.getenv(
            "DATABASE_URL", "postgresql://user_ans:senha_secreta_ans@localhost:5432/empresa_x")

        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar no PostgreSQL: {e}")
        return None
