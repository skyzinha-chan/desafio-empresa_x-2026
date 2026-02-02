# backend/app/services/step3_db_ingestion.py

import os
import pandas as pd
import logging
from app.db.connection import get_db_connection

# Configuração de Logs para vermos o que está acontecendo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Step3DBIngestion:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # --- LÓGICA HÍBRIDA (DOCKER vs LOCAL) ---
    possible_root_local = os.path.abspath(os.path.join(BASE_DIR, "../../../"))
    possible_root_docker = os.path.abspath(os.path.join(BASE_DIR, "../../"))

    # Verifica onde está a pasta 'scripts_sql' (que sempre existe na raiz)
    if os.path.exists(os.path.join(possible_root_local, "scripts_sql")):
        ROOT_DIR = possible_root_local
    else:
        ROOT_DIR = possible_root_docker

    DATA_DIR = os.path.join(ROOT_DIR, "data")
    SQL_DIR = os.path.join(ROOT_DIR, "scripts_sql")
    # ----------------------------------------

    # Arquivos CSV
    FILE_CONSOLIDADO = os.path.join(DATA_DIR, "consolidado_despesas.csv")
    FILE_CADOP = os.path.join(DATA_DIR, "Relatorio_Cadop.csv")
    FILE_AGREGADO = os.path.join(DATA_DIR, "despesas_agregadas.csv")
    # Arquivo SQL
    FILE_CREATE_TABLES = os.path.join(SQL_DIR, "create_tables.sql")

    @classmethod
    def execute(cls):
        """Executa o pipeline completo da Etapa 3."""
        print("\n🚀 [ETAPA 3] Ingestão no PostgreSQL...")

        if not os.path.exists(cls.FILE_CONSOLIDADO) or not os.path.exists(cls.FILE_CADOP):
            print(
                "❌ Arquivos necessários não encontrados na pasta data/. Rode Etapa 1 e 2.")
            return

        # 1. Garantir que as tabelas existem (Lê o arquivo .sql e executa)
        cls.criar_tabelas()

        # 2. Processar Operadoras 
        cls.processar_e_inserir_operadoras()

        # 3. Processar Despesas (Brutas)
        cls.processar_e_inserir_despesas()

        # 4. Inserir Agregados 
        cls.processar_e_inserir_agregados()

        print("✅ [FIM ETAPA 3] Banco de dados populado com sucesso!")


    @classmethod
    def criar_tabelas(cls):
        """Lê o arquivo create_tables.sql e executa no banco"""
        print("🏗️ Verificando estrutura do banco...")
        conn = get_db_connection()
        if not conn:
            return

        try:
            with open(cls.FILE_CREATE_TABLES, "r", encoding="utf-8") as f:
                sql_script = f.read()

            with conn.cursor() as cursor:
                cursor.execute(sql_script)
                conn.commit()
                logger.info("🚀 Tabelas criadas/verificadas com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
        finally:
            conn.close()


    @classmethod
    def processar_e_inserir_operadoras(cls):
        print("📚 Lendo e tratando arquivo CADOP...")
        try:
            # Lendo CADOP com tratamento de encoding para corrigir o "SAÚDE"
            # 1. Resiliência de Encoding
            try:
                cadop = pd.read_csv(cls.FILE_CADOP, sep=';', encoding='utf-8', dtype=str, quotechar='"')
            except UnicodeDecodeError:
                logger.warning("⚠️ Falha com UTF-8, tentando Latin-1...")
                cadop = pd.read_csv(cls.FILE_CADOP, sep=';', encoding='latin-1', dtype=str, quotechar='"')

            # 2. Normalização de Colunas
            cadop.columns = [c.upper().strip() for c in cadop.columns]
            
            # 3. Mapeamento Inteligente das Colunas (Acha a coluna certa mesmo se o nome variar)
            try:
                col_cnpj = next(c for c in cadop.columns if 'CNPJ' in c)
                col_razao = next(
                    c for c in cadop.columns if 'RAZAO' in c or 'RAZÃO' in c)
                # Pega REGISTRO_OPERADORA mas evita DATA_REGISTRO
                col_reg = next(
                    c for c in cadop.columns if 'REGISTRO' in c and 'DATA' not in c)
                col_mod = next(c for c in cadop.columns if 'MODALIDADE' in c)
                col_uf = next(c for c in cadop.columns if 'UF' in c)
            except StopIteration:
                logger.error(
                    "❌ Colunas obrigatórias não encontradas no CADOP.")
                return

            # 4. Limpeza Crítica de Strings
            cadop['CNPJ_CLEAN'] = cadop[col_cnpj].str.replace(r'\D', '', regex=True).str.zfill(14)
            cadop['REG_CLEAN'] = cadop[col_reg].str.replace(r'\D', '', regex=True).str.zfill(6)
            
            # 5. Preparar DataFrame final
            df_ops = pd.DataFrame()
            df_ops['registro_ans'] = cadop['REG_CLEAN']
            df_ops['cnpj'] = cadop['CNPJ_CLEAN']
            df_ops['razao_social'] = cadop[col_razao]
            df_ops['modalidade'] = cadop[col_mod]
            df_ops['uf'] = cadop[col_uf]

            # Preenche colunas extras (Opcionais)
            # Mapeamos Logradouro, Bairro, etc se existirem
            extras = {
                'logradouro': 'LOGRADOURO', 'numero': 'NUMERO',
                'complemento': 'COMPLEMENTO', 'bairro': 'BAIRRO',
                'cidade': 'CIDADE', 'cep': 'CEP',
                'telefone': 'TELEFONE', 'email': 'ELETRONICO'  # Endereco_eletronico
            }

            for db_col, csv_keyword in extras.items():
                try:
                    csv_col = next(
                        c for c in cadop.columns if csv_keyword in c)
                    df_ops[db_col] = cadop[csv_col]
                except StopIteration:
                    df_ops[db_col] = None

            # Colunas que não existem no CSV
            df_ops['nome_fantasia'] = None               
            # 6. Remove duplicados (CNPJ é PK)
            df_ops = df_ops.drop_duplicates(subset=['cnpj'])
            colunas_ordenadas = [
                'registro_ans', 'cnpj', 'razao_social', 'nome_fantasia',
                'modalidade', 'logradouro', 'numero', 'complemento',
                'bairro', 'cidade', 'uf', 'cep', 'telefone', 'email'
            ]
            df_ops = df_ops[colunas_ordenadas]
            # --- INSERÇÃO NO POSTGRES ---
            cls._bulk_insert_operadoras(df_ops)
            print(f"    ✅ {len(df_ops)} operadoras inseridas.")
        except Exception as e:
            print(f"❌ Erro no processamento do CADOP: {e}")


    @classmethod
    def _bulk_insert_operadoras(cls, df):
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            # 1. Conexão com Banco
            cursor = conn.cursor()
            print(f"🔌 Conectado ao banco")
            logger.info(
                f"🚀 Inserindo/Atualizando {len(df)} operadoras no Postgres...")

            # Query Postgres com ON CONFLICT (Atualiza se já existir)
            query = """
                INSERT INTO operadoras (
                    registro_ans, cnpj, razao_social, nome_fantasia, 
                    modalidade, logradouro, numero, complemento, 
                    bairro, cidade, uf, cep, telefone, email
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cnpj) DO UPDATE SET 
                    razao_social = EXCLUDED.razao_social,
                    data_atualizacao = CURRENT_TIMESTAMP;
            """
            # Prepara dados (None em vez de NaN)
            dados = df.where(pd.notnull(df), None).values.tolist()
            cursor.executemany(query, dados)
            conn.commit()
            logger.info("✅ Operadoras sincronizadas!")
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro SQL Operadoras: {e}")
        finally:
            conn.close()


    @classmethod
    def processar_e_inserir_despesas(cls):
        # 4. Inserir Despesas (Fato)
        print("💰 Inserindo Despesas...")
        try:
            df_desp = pd.read_csv(cls.FILE_CONSOLIDADO, sep=';', dtype=str)
            
            # Limpeza e Conversão
            df_desp['cnpj_operadora'] = df_desp['CNPJ'].str.replace(r'\D', '', regex=True).str.zfill(14)
            # Se vier com vírgula converte, se vier com ponto mantém
            df_desp['valor_despesa'] = pd.to_numeric(
                df_desp['VALORDESPESAS'].str.replace(',', '.'), errors='coerce')
            
            # Converte Ano e Trimestre para int seguro
            df_desp['ANO'] = pd.to_numeric(
                df_desp['ANO'], errors='coerce').fillna(0).astype(int)
            df_desp['TRIMESTRE'] = pd.to_numeric(
                df_desp['TRIMESTRE'], errors='coerce').fillna(1).astype(int)

            # Função de Data Segura
            def get_data(row):
                try:
                    mes = int(row['TRIMESTRE']) * 3 - 2
                    return f"{int(row['ANO']):04d}-{mes:02d}-01"
                except:
                    return None

            df_desp['data_evento'] = df_desp.apply(get_data, axis=1)
            # Remove datas inválidas
            df_desp = df_desp.dropna(subset=['data_evento'])

            # Montagem Final
            df_final = pd.DataFrame()
            df_final['data_evento'] = df_desp['data_evento']
            df_final['cnpj_operadora'] = df_desp['cnpj_operadora']
            df_final['cd_conta_contabil'] = df_desp.get('CONTA', '411')
            df_final['descricao'] = df_desp.get(
                'DESCRICAO', 'Despesa Assistencial')
            df_final['valor_despesa'] = df_desp['valor_despesa']
            df_final['ano'] = df_desp['ANO']
            df_final['trimestre'] = df_desp['TRIMESTRE']

            # --- FILTRAR DESPESAS ÓRFÃS ---
            conn = get_db_connection()
            if not conn:
                return

            cursor = conn.cursor()
            print("🔍 Buscando CNPJs válidos no banco...")
            cursor.execute("SELECT cnpj FROM operadoras")
            # Cria um conjunto (set) com todos os CNPJs que existem no banco
            valid_cnpjs = set(row[0] for row in cursor.fetchall())
            conn.close()

            # Filtra: Mantém apenas despesas cujo CNPJ está no conjunto de válidos
            total_antes = len(df_final)
            df_final = df_final[df_final['cnpj_operadora'].isin(valid_cnpjs)]
            total_depois = len(df_final)

            diff = total_antes - total_depois
            if diff > 0:
                logger.warning(
                    f"⚠️ {diff} despesas ignoradas pois a operadora não está no CADOP (Órfãs).")

            # Inserir apenas as válidas
            cls._bulk_insert_despesas(df_final)
            print(f"    ✅ {len(df_final)} registros de despesas inseridos.")

        except Exception as e:
            print(f"❌ Erro no processamento das Despesas: {e}")


    @classmethod
    def _bulk_insert_despesas(cls, df):
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            logger.info(
                f"🚀 Inserindo {len(df)} despesas no Postgres...")

            query = """
                INSERT INTO despesas (
                    data_evento, cnpj_operadora, cd_conta_contabil, 
                    descricao, valor_despesa, ano, trimestre
                ) VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            dados = df.where(pd.notnull(df), None).values.tolist()
            cursor.executemany(query, dados)
            conn.commit()
            logger.info("✅ Despesas inseridas com sucesso!")
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro SQL Despesas: {e}")
        finally:
            conn.close()


    @classmethod
    def processar_e_inserir_agregados(cls):
        print("📊 Importando Tabela Agregada (Item 3.1)...")
        try:
            # Lê o arquivo gerado na etapa 2
            df_agg = pd.read_csv(cls.FILE_AGREGADO, sep=';')

            # Mapeia colunas do CSV para o Banco
            # CSV: RAZAO_FINAL;UF;TOTAL;MEDIA;DESVIO
            # DB: razao_social, uf, total_despesas, media_trimestral, desvio_padrao

            df_final = pd.DataFrame()
            df_final['razao_social'] = df_agg['RAZAO_FINAL']
            df_final['uf'] = df_agg['UF']
            df_final['total_despesas'] = df_agg['TOTAL']
            df_final['media_trimestral'] = df_agg['MEDIA']
            df_final['desvio_padrao'] = df_agg['DESVIO'].fillna(
                0)  # Trata NULL

            # Chama o método especialista em inserir
            cls._bulk_insert_agregados(df_final)

        except Exception as e:
            logger.error(f"❌ Erro ao processar agregados: {e}")


    @classmethod
    def _bulk_insert_agregados(cls, df_final):
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            logger.info(f"🚀 Inserindo {len(df_final)} registros agregados...")

            # Limpa tabela antes (Overwrite strategy para snapshot)
            cursor.execute("TRUNCATE TABLE despesas_agregadas")

            query = """
                INSERT INTO despesas_agregadas (
                    razao_social, uf, total_despesas,
                    media_trimestral, desvio_padrao
                ) VALUES (%s, %s, %s, %s, %s)
            """
            dados = df_final.values.tolist()
            cursor.executemany(query, dados)
            conn.commit()
            logger.info("✅ Agregados importados com sucesso!")          
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao importar agregados: {e}")
        finally:
            conn.close()

            
if __name__ == "__main__":
    Step3DBIngestion.execute()