import pandas as pd
import zipfile
import shutil
import os


class DataProcessor:
    """
    Servico responsavel pelo processamento e normalizacao de grandes volumes de dados da ANS.
    Implementa processamento incremental para otimizacao de memoria.
    """
    @classmethod
    def processar_e_normalizar(cls, caminhos_zips, data_dir):
        """
        Extrai ZIPs, identifica arquivos de despesas (411) e normaliza colunas.
        Retorna lista de DataFrames.
        """
        temp_extract_dir = os.path.join(data_dir, "temp_extract")
        os.makedirs(temp_extract_dir, exist_ok=True)

        dados_consolidados = []

        for zip_path in caminhos_zips:
            print(f"📦 Extraindo: {os.path.basename(zip_path)}")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_extract_dir)

                # 1. Varredura dos arquivos extraidos
                for root, dirs, files in os.walk(temp_extract_dir):
                    for file in files:
                        if file.lower().endswith(('.csv', '.xlsx', '.xls')):
                            caminho_arquivo = os.path.join(root, file)

                            try:
                                # --- PASSO A: Inspecao Rapida (Duck Typing) ---
                                # 1. Identificação (Lê apenas o cabeçalho)
                                # A ANS muda o encoding as vezes (latin-1 ou utf-8)
                                try:
                                    header = pd.read_csv(
                                        caminho_arquivo, sep=';', encoding='latin-1', nrows=0)
                                except:
                                    header = pd.read_csv(
                                        caminho_arquivo, sep=';', encoding='utf-8', nrows=0)
                                    
                                colunas_reais = [str(c).upper().strip()
                                                 for c in header.columns]

                                # Criterios de Identificacao
                                is_alvo = 'CD_CONTA_CONTABIL' in colunas_reais or 'VL_DESPESA' in colunas_reais
                                has_values = any(c in colunas_reais for c in [
                                                 'VL_EVENTO', 'VL_DESPESA', 'VL_SALDO_FINAL'])

                                # --- PASSO B: Decisao de Processamento ---
                                if is_alvo or has_values:
                                    print(
                                        f"  🎯 Alvo identificado pelo conteúdo: {file}")

                                    # --- PASSO C: Processamento Incremental (Chunks) ---
                                    # Processamos em pedacos para suportar arquivos de 700k+ linhas
                                    chunks = pd.read_csv(
                                        caminho_arquivo,
                                        sep=';',
                                        encoding='latin-1',
                                        chunksize=100000,
                                        dtype=str,
                                        decimal=','  # Garante que pontos decimais sejam lidos corretamente
                                    )

                                    for chunk in chunks:
                                        chunk.columns = [
                                            str(c).strip().upper() for c in chunk.columns]

                                        # --- 3. Filtro de Sinistros/Eventos (Regra de Negocio) ---
                                        # Filtramos contas que iniciam com 411 (Padrao ANS para Eventos/Sinistros)
                                        if 'CD_CONTA_CONTABIL' in chunk.columns:
                                            # Remove pontos da conta (ex: 4.1.1 -> 411) para filtrar
                                            conta_limpa = chunk['CD_CONTA_CONTABIL'].str.replace(
                                                r'\D', '', regex=True)
                                            mask = (conta_limpa == '411')
                                            df_filtrado = chunk[mask].copy()
                                        else:
                                            # Fallback: Tenta achar "EVENTO" na descrição
                                            mask = chunk.apply(lambda x: x.str.contains(
                                                'EVENTO', case=False, na=False)).any(axis=1)
                                            df_filtrado = chunk[mask].copy()

                                        if df_filtrado.empty:
                                            continue

                                        # Mapeamento e Normalizacao ---
                                        mapeamento = {
                                            'REG_ANS': 'REGISTRO_ANS',
                                            'CD_OPERADORA': 'REGISTRO_ANS',
                                            'NR_CNPJ': 'CNPJ',
                                            'CNPJ': 'CNPJ',
                                            'NM_RAZAO_SOCIAL': 'RAZAOSOCIAL',
                                            'RAZAO_SOCIAL': 'RAZAOSOCIAL',
                                            'VL_SALDO_FINAL': 'VALORDESPESAS',
                                            'VL_SALDO_INICIAL': 'VALOR_INICIAL'  # Só para garantir
                                        }
                                        df_filtrado.rename(
                                            columns=mapeamento, inplace=True)

                                        # Se não tiver CNPJ, usamos o Registro ANS provisoriamente (será corrigido na Etapa 2)
                                        if 'CNPJ' not in df_filtrado.columns and 'REGISTRO_ANS' in df_filtrado.columns:
                                            df_filtrado['CNPJ'] = df_filtrado['REGISTRO_ANS']

                                        # Garante que temos a coluna chave
                                        if 'REGISTRO_ANS' not in df_filtrado.columns:
                                            # Tenta achar a primeira coluna que parece ID
                                            df_filtrado['REGISTRO_ANS'] = df_filtrado.iloc[:, 0]


                                        # Se RAZAOSOCIAL nao existir no arquivo, criamos como N/A para consolidar
                                        if 'RAZAOSOCIAL' not in df_filtrado.columns:
                                            df_filtrado['RAZAOSOCIAL'] = "NAO DISPONIVEL NO ARQUIVO FONTE"

                                        # Metadados do Arquivo
                                        nome_zip = os.path.basename(
                                            zip_path).upper()
                                        # Tenta extrair ano
                                        df_filtrado['ANO'] = nome_zip[-8:-
                                                                  4] if '20' in nome_zip else '0000'
                                        df_filtrado['TRIMESTRE'] = nome_zip[0] if 'T' in nome_zip else '0'

                                        # Garantir colunas minimas para o CSV final
                                        cols_finais = [
                                            'CNPJ', 'RAZAOSOCIAL', 'ANO', 'TRIMESTRE', 'VALORDESPESAS']
                                        # Garante que as colunas existem
                                        for c in cols_finais:
                                            if c not in df_filtrado.columns:
                                                df_filtrado[c] = ''
                                        dados_consolidados.append(
                                            df_filtrado[[c for c in cols_finais if c in df_filtrado.columns]])

                                    print(
                                        f"    ✅ Sucesso: Dados extraidos de {file}")

                                else:
                                    # Opcional:
                                    print(
                                        f"  ⏭️ Ignorado: {file}")
                                    pass

                            except Exception as e:
                                print(
                                    f"    ⚠️ Erro ao processar conteúdo de {file}: {e}")

                # Limpar pasta temporária após cada ZIP para economizar espaço
                shutil.rmtree(temp_extract_dir)
                os.makedirs(temp_extract_dir, exist_ok=True)

            except Exception as e:
                print(f"❌ Falha ao processar ZIP {zip_path}: {e}")

        # Limpeza final
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)

        return dados_consolidados
