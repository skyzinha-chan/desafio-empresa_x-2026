import os
import pandas as pd
import zipfile
from dotenv import load_dotenv

# Imports relativos
try:
    from ans_scrapper import ANSScraper
    from data_processor import DataProcessor
except ImportError:
    from app.services.ans_scrapper import ANSScraper
    from app.services.data_processor import DataProcessor

load_dotenv()

class Step1ETL:
    BASE_URL = os.getenv("ANS_DATA_SOURCE_URL", "")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # --- LÓGICA HÍBRIDA (DOCKER vs LOCAL) ---
    # Tenta voltar 3 níveis (Estrutura Local: backend/app/services -> Raiz)
    possible_root_local = os.path.abspath(os.path.join(BASE_DIR, "../../../"))
    # Tenta voltar 2 níveis (Estrutura Docker: app/services -> /app)
    possible_root_docker = os.path.abspath(os.path.join(BASE_DIR, "../../"))

    # Verifica qual caminho contém a pasta 'data'. Se achar a local, usa a local.
    # Caso contrário, assume que estamos no Docker.
    if os.path.exists(os.path.join(possible_root_local, "data")):
        ROOT_DIR = possible_root_local
    else:
        ROOT_DIR = possible_root_docker

    DATA_DIR = os.path.join(ROOT_DIR, "data")

    @classmethod
    def execute(cls):
        print("🚀 [ETAPA 1] Iniciando Integração e Consolidação...")
        
        # 1. Identificar e Baixar ZIPs
        urls = ANSScraper.identificar_arquivos_trimestrais(cls.BASE_URL)
        zips = ANSScraper.baixar_arquivos(urls, cls.DATA_DIR)
        
        if not zips:
            print("❌ Nenhum arquivo baixado.")
            return

        # 2. Processar (Apenas extração)
        print("\n⚙️ Processando arquivos brutos...")
        lista_dfs = DataProcessor.processar_e_normalizar(zips, cls.DATA_DIR)
        
        if not lista_dfs:
            print("❌ Nenhum dado encontrado.")
            return

        # 3. Consolidação e Tratamento Básico (Remover duplicados exatos)
        print("\n📊 Consolidando...")
        df_final = pd.concat(lista_dfs, ignore_index=True)

        # Tratamento de valores numéricos (Vírgula -> Ponto)
        df_final['VALORDESPESAS'] = df_final['VALORDESPESAS'].astype(str).str.replace(',', '.')
        df_final['VALORDESPESAS'] = pd.to_numeric(df_final['VALORDESPESAS'], errors='coerce').fillna(0)
        
        # Filtra valores zerados (conforme pedido na Análise de Inconsistências)
        df_final = df_final[df_final['VALORDESPESAS'] > 0]

        # Salva o arquivo "Bruto/Consolidado"
        csv_path = os.path.join(cls.DATA_DIR, "consolidado_despesas.csv")
        df_final.to_csv(csv_path, index=False, sep=';', encoding='utf-8')
        
        zip_path = os.path.join(cls.DATA_DIR, "consolidado_despesas.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(csv_path, arcname="consolidado_despesas.csv")

        print(f"✅ [FIM ETAPA 1] Arquivo gerado: {zip_path}")
        print("⚠️ Nota: Este arquivo pode conter 'NAO DISPONIVEL' na Razão Social. Isso será corrigido na Etapa 2.")

if __name__ == "__main__":
    Step1ETL.execute()