import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class Step3DBIngestion:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "../../../data")
    DB_PATH = os.path.join(DATA_DIR, "empresa_x.db") # Banco local SQLite

    # Arquivos gerados nas etapas anteriores
    FILE_CONSOLIDADO = os.path.join(DATA_DIR, "consolidado_despesas.csv")
    FILE_CADOP = os.path.join(DATA_DIR, "Relatorio_Cadop.csv")

    @classmethod
    def execute(cls):
        print("\n🚀 [ETAPA 3] Ingestão no Banco de Dados...")

        if not os.path.exists(cls.FILE_CONSOLIDADO) or not os.path.exists(cls.FILE_CADOP):
            print("❌ Arquivos necessários não encontrados. Rode Etapa 1 e 2.")
            return

        # 1. Conexão com Banco
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        print(f"🔌 Conectado ao banco: {cls.DB_PATH}")

        # 2. Criar Tabelas (DDL)
        # Adaptado para SQLite (Postgres usaria SERIAL em vez de AUTOINCREMENT)
        cursor.executescript("""
            -- 1. Tabela Dimensão: Operadoras
            CREATE TABLE IF NOT EXISTS operadoras (
                registro_ans TEXT,
                cnpj TEXT PRIMARY KEY,
                razao_social TEXT,
                nome_fantasia TEXT,
                modalidade TEXT,
                logradouro TEXT,
                numero TEXT,
                complemento TEXT,
                bairro TEXT,
                cidade TEXT,
                uf TEXT,
                cep TEXT,
                telefone TEXT,
                email TEXT,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_ops_razao ON operadoras(razao_social);
            CREATE INDEX IF NOT EXISTS idx_ops_uf ON operadoras(uf);

            -- 2. Tabela Fato: Despesas Financeiras
            CREATE TABLE IF NOT EXISTS despesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT, -- Ajustado: SQLite usa AUTOINCREMENT, não SERIAL
                cnpj_operadora TEXT,
                ano INTEGER NOT NULL,
                trimestre INTEGER NOT NULL,
                valor_despesa REAL, -- Ajustado: SQLite usa REAL para valores decimais
                data_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cnpj_operadora) REFERENCES operadoras(cnpj)
            );

            CREATE INDEX IF NOT EXISTS idx_despesas_periodo ON despesas(ano, trimestre);
            CREATE INDEX IF NOT EXISTS idx_despesas_valor ON despesas(valor_despesa);
        """)
        conn.commit()

        # 3. Inserir Operadoras (Dimensão)
        print("📚 Inserindo Operadoras...")
        try:
            # Lendo CADOP com tratamento de encoding para corrigir o "SAÚDE"
            try:
                cadop = pd.read_csv(cls.FILE_CADOP, sep=';', encoding='utf-8', dtype=str, quotechar='"')
            except:
                cadop = pd.read_csv(cls.FILE_CADOP, sep=';', encoding='latin-1', dtype=str, quotechar='"')

            cadop.columns = [c.upper().strip() for c in cadop.columns]
            
            # Mapeamento de colunas
            col_cnpj = next(c for c in cadop.columns if 'CNPJ' in c)
            col_razao = next(c for c in cadop.columns if 'RAZAO' in c)
            col_uf = next(c for c in cadop.columns if 'UF' in c)
            col_reg = next(c for c in cadop.columns if 'REGISTRO' in c)
            col_mod = next(c for c in cadop.columns if 'MODALIDADE' in c)

            # Limpeza
            cadop['CNPJ_CLEAN'] = cadop[col_cnpj].str.replace(r'\D', '', regex=True).str.zfill(14)
            cadop['REG_CLEAN'] = cadop[col_reg].str.replace(r'\D', '', regex=True).str.zfill(6)
            
            # Preparar DataFrame para o Banco
            df_ops = cadop[['CNPJ_CLEAN', 'REG_CLEAN', col_razao, col_uf, col_mod]].copy()
            df_ops.columns = ['cnpj', 'registro_ans', 'razao_social', 'uf', 'modalidade']
            
            # Remove duplicados (CNPJ é PK)
            df_ops = df_ops.drop_duplicates(subset=['cnpj'])
            
            # Bulk Insert
            df_ops.to_sql('operadoras', conn, if_exists='replace', index=False)
            print(f"    ✅ {len(df_ops)} operadoras inseridas.")

        except Exception as e:
            print(f"❌ Erro ao inserir operadoras: {e}")

        # 4. Inserir Despesas (Fato)
        print("💰 Inserindo Despesas...")
        try:
            df_desp = pd.read_csv(cls.FILE_CONSOLIDADO, sep=';', dtype=str)
            
            # Limpeza
            df_desp['cnpj_operadora'] = df_desp['CNPJ'].str.replace(r'\D', '', regex=True).str.zfill(14)
            df_desp['valor_despesa'] = pd.to_numeric(df_desp['VALORDESPESAS'], errors='coerce')
            
            # Seleção
            df_final = df_desp[['cnpj_operadora', 'ANO', 'TRIMESTRE', 'valor_despesa']].copy()
            df_final.columns = ['cnpj_operadora', 'ano', 'trimestre', 'valor_despesa']
            
            df_final.to_sql('despesas', conn, if_exists='append', index=False)
            print(f"    ✅ {len(df_final)} registros de despesas inseridos.")

        except Exception as e:
            print(f"❌ Erro ao inserir despesas: {e}")

        conn.close()
        print("✅ [FIM ETAPA 3] Banco de dados populado com sucesso!")

if __name__ == "__main__":
    Step3DBIngestion.execute()