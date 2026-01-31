import os
import zipfile
import pandas as pd
from dotenv import load_dotenv

# Importação relativa para os módulos vizinhos
from ans_scrapper import ANSScraper
from data_processor import DataProcessor

load_dotenv()  # Carrega as variáveis do .env


class ANSService:
    """
    Serviço Orquestrador: Centraliza configurações e coordena o fluxo ETL.
    """

    # Buscamos do .env. Se não existir, usamos uma string vazia como fallback
    BASE_URL = os.getenv("ANS_DATA_SOURCE_URL", "")
    DATA_DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../../../data"))


    @classmethod
    def consolidar_e_analisar(cls, lista_dfs):
        """
        Consolida os dados, trata inconsistências e gera o ZIP final (Item 1.3).
        """
        if not lista_dfs:
            print("⚠️ Sem dados para consolidar.")
            return

        print("\n📊 Iniciando consolidação e análise de inconsistências...")

        # 1. Juntar todos os DataFrames
        df_final = pd.concat(lista_dfs, ignore_index=True)

        # --- TRATAMENTO DE INCONSISTÊNCIAS ---

        # A. Tratar Valores (Ignorar ou corrigir negativos/zerados)
        # Decisão técnica: Converter para numérico e filtrar apenas > 0
        df_final['VALORDESPESAS'] = pd.to_numeric(
            df_final['VALORDESPESAS'], errors='coerce').fillna(0)
        iniciais = len(df_final)
        df_final = df_final[df_final['VALORDESPESAS'] > 0]
        print(
            f"  🧹 Valores: Removidas {iniciais - len(df_final)} linhas com valores inválidos ou <= 0.")

        # B. Tratar CNPJs e Razão Social (Conflitos)
        # Decisão: Manter a primeira Razão Social encontrada para cada CNPJ (Padronização)
        df_final = df_final.sort_values(by=['CNPJ', 'RAZAOSOCIAL'])
        df_final['RAZAOSOCIAL'] = df_final.groupby(
            'CNPJ')['RAZAOSOCIAL'].transform('first')

        # C. Remover Duplicados Reais (Mesmo CNPJ, Ano, Trimestre e Valor)
        df_final = df_final.drop_duplicates()

        # 2. Gerar o CSV Final
        csv_path = os.path.join(cls.DATA_DIR, "consolidado_despesas.csv")
        df_final.to_csv(csv_path, index=False, sep=';', encoding='utf-8-sig')

        # 3. Compactar em ZIP (conforme pedido)
        zip_final_path = os.path.join(cls.DATA_DIR, "consolidado_despesas.zip")
        with zipfile.ZipFile(zip_final_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(csv_path, arcname="consolidado_despesas.csv")

        print(f"✅ Arquivo final gerado: {zip_final_path}")
        return zip_final_path

            
# Exemplo simples para teste manual
if __name__ == "__main__":
    # 1. Identificar (Passamos a URL como argumento)
    urls = ANSScraper.identificar_arquivos_trimestrais(ANSService.BASE_URL)

    if urls:
        # 2. Baixar (Passamos a pasta de destino como argumento)
        caminhos_zips = ANSScraper.baixar_arquivos(urls, ANSService.DATA_DIR)

        if caminhos_zips:
            print("\n🧪 Iniciando processamento dos dados...")
            # 3. Processar (Passamos a pasta de dados para o processador saber onde criar a temp)
            lista_dataframes = DataProcessor.processar_e_normalizar(
                caminhos_zips, ANSService.DATA_DIR)

            if lista_dataframes:
                # 4. Consolidar via SERVICE (onde a função ficou)
                ANSService.consolidar_e_analisar(lista_dataframes)
                print(
                    f"✅ Sucesso: {len(lista_dataframes)} arquivos de despesas foram carregados na memória.")
                # Aqui você já tem os dados prontos para a Consolidação (Item 1.3)
            else:
                print(
                    "⚠️ Nenhum arquivo de despesas/sinistros foi encontrado dentro dos ZIPs.")
    else:
        print("❌ Não foi possível encontrar os links para download.")   
