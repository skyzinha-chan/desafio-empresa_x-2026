import pandas as pd
import os
import zipfile
from dotenv import load_dotenv

try:
    from ans_scrapper import ANSScraper
except ImportError:
    from app.services.ans_scrapper import ANSScraper

load_dotenv()

class Step2Transformation:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "../../../data")
    URL_CADOP = os.getenv("ANS_CADASTRO_OPERADORAS_URL", "")

    @classmethod
    def execute(cls):
        print("\n🚀 [ETAPA 2] Transformação, Validação e Enriquecimento...")
        
        input_csv = os.path.join(cls.DATA_DIR, "consolidado_despesas.csv")
        if not os.path.exists(input_csv):
            print("❌ Execute a Etapa 1 primeiro!")
            return

        # 1. Carregar Consolidado da Etapa 1
        print("📖 Lendo consolidado da Etapa 1...")
        df = pd.read_csv(input_csv, sep=';', dtype=str)

        # 2. Baixar CADOP
        caminho_cadop = ANSScraper.baixar_cadop(cls.DATA_DIR, cls.URL_CADOP)
        if not caminho_cadop:
            print("❌ Falha ao baixar CADOP. Abortando Etapa 2.")
            return

        # 3. Carregar e Preparar CADOP para Join
        print("📚 Preparando Cadastro de Operadoras...")
        cadop = pd.read_csv(caminho_cadop, sep=';', encoding='latin-1', dtype=str, quotechar='"')
        cadop.columns = [c.upper().strip() for c in cadop.columns]

        # Identificar colunas do CADOP
        col_reg = next(c for c in cadop.columns if 'REGISTRO' in c)
        col_cnpj = next(c for c in cadop.columns if 'CNPJ' in c)
        col_razao = next(c for c in cadop.columns if 'RAZAO' in c)
        col_uf = next(c for c in cadop.columns if 'UF' in c)
        col_mod = next(c for c in cadop.columns if 'MODALIDADE' in c)

        # Limpeza Chaves CADOP
        cadop['KEY_JOIN'] = cadop[col_reg].str.replace(r'\D', '', regex=True).str.zfill(6)
        cadop['CNPJ_CLEAN'] = cadop[col_cnpj].str.replace(r'\D', '', regex=True).str.zfill(14)
        
        # Selecionar apenas o necessário (Lookup Table)
        cadop_lookup = cadop[['KEY_JOIN', 'CNPJ_CLEAN', col_razao, col_uf, col_mod]].copy()
        cadop_lookup.columns = ['KEY', 'CNPJ_REAL', 'RAZAO_REAL', 'UF', 'MODALIDADE']

        # 4. Preparar Consolidado para Join
        # O consolidado da Etapa 1 pode ter CNPJ ou REG_ANS na coluna 'CNPJ'
        # Vamos assumir que é o REG_ANS (comum nos arquivos 411) e limpar
        df['KEY'] = df['CNPJ'].str.replace(r'\D', '', regex=True).str.zfill(6)

        # 5. JOIN (Enriquecimento)
        print("🔗 Cruzando dados (Join Consolidado x CADOP)...")
        df_merged = pd.merge(df, cadop_lookup, on='KEY', how='left')

        # 6. Substituição e Correção
        # Se achou no CADOP, usa o dado do CADOP. Se não, mantém o original (com flag)
        df_merged['CNPJ_FINAL'] = df_merged['CNPJ_REAL'].fillna(df_merged['CNPJ'])
        df_merged['RAZAO_FINAL'] = df_merged['RAZAO_REAL'].fillna("NAO ENCONTRADA NO CADASTRO")
        df_merged['UF'] = df_merged['UF'].fillna("N/I")
        df_merged['MODALIDADE'] = df_merged['MODALIDADE'].fillna("DESCONHECIDA")

        # 6.1. Atualizar o consolidado com dados reais de 14 dígitos (Mão na massa!)
        # Isso garante que o banco de dados (Etapa 3) consiga ligar as tabelas corretamente.
        print("💾 Atualizando consolidado com CNPJs de 14 dígitos e Nomes Reais...")

        # Substituímos as colunas originais pelas enriquecidas do CADOP
        df_merged['CNPJ'] = df_merged['CNPJ_FINAL']
        df_merged['RAZAOSOCIAL'] = df_merged['RAZAO_FINAL']

        # Sobrescrevemos o arquivo CSV que o Banco de Dados (Step 3) vai ler
        # Mantendo as colunas exigidas no item 1.3 do desafio
        cols_finais_consolidado = [
            'CNPJ', 'RAZAOSOCIAL', 'ANO', 'TRIMESTRE', 'VALORDESPESAS']
        df_merged[cols_finais_consolidado].to_csv(
            input_csv, index=False, sep=';', encoding='utf-8-sig')

        # 7. Agregação (Item 2.3)
        print("📊 Calculando Estatísticas...")
        df_merged['VALORDESPESAS'] = pd.to_numeric(df_merged['VALORDESPESAS'], errors='coerce').fillna(0)
        
        agregado = df_merged.groupby(['RAZAO_FINAL', 'UF'])['VALORDESPESAS'].agg(
            TOTAL=('sum'),  # Total de despesas
            MEDIA=('mean'),  # Média por trimestre
            DESVIO=('std')  # Desvio padrão
        ).reset_index().sort_values(by='TOTAL', ascending=False)

        # 8. Salvar
        output_csv = os.path.join(cls.DATA_DIR, "despesas_agregadas.csv")
        agregado.to_csv(output_csv, index=False, sep=';', encoding='utf-8-sig')
        
        output_zip = os.path.join(cls.DATA_DIR, "Teste_Talita_Mendonca.zip")
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(output_csv, arcname="despesas_agregadas.csv")

        print(f"✅ [FIM ETAPA 2] Arquivo final: {output_zip}")
        print(agregado.head())

if __name__ == "__main__":
    Step2Transformation.execute()