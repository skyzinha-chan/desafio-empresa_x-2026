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
        Extrai, filtra arquivos de despesas via chunks e normaliza os dados.
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
                                # Lemos apenas o cabecalho (nrows=0) para decidir se processamos o arquivo
                                header = pd.read_csv(
                                    caminho_arquivo, sep=';', encoding='latin-1', nrows=0)
                                colunas_reais = [str(c).upper()
                                                 for c in header.columns]

                                # Criterios de Identificacao
                                is_contabil = 'CD_CONTA_CONTABIL' in colunas_reais
                                has_values = any(c in colunas_reais for c in [
                                                 'VL_EVENTO', 'VL_DESPESA', 'VL_SALDO_FINAL'])

                                # --- PASSO B: Decisao de Processamento ---
                                if is_contabil or has_values:
                                    print(
                                        f"  🎯 Alvo identificado pelo conteúdo: {file}")

                                    # --- PASSO C: Processamento Incremental (Chunks) ---
                                    # Processamos em pedacos para suportar arquivos de 700k+ linhas                             
                                    chunks = pd.read_csv(
                                        caminho_arquivo,
                                        sep=';',
                                        encoding='latin-1',
                                        chunksize=100000,
                                        decimal=',',  # Trata "99024,72" como numero
                                        dtype={'CD_CONTA_CONTABIL': str,
                                            'REG_ANS': str, 'NR_CNPJ': str}
                                    )

                                    for chunk in chunks:
                                        chunk.columns = [
                                            str(c).strip().upper() for c in chunk.columns]

                                        # --- 3. Filtro de Sinistros/Eventos (Regra de Negocio) ---
                                        # Filtramos contas que iniciam com 411 (Padrao ANS para Eventos/Sinistros)
                                        if is_contabil:
                                            mask = chunk['CD_CONTA_CONTABIL'].str.startswith(
                                                '411', na=False)
                                        else:
                                            # Fallback para outros formatos que usam palavras-chave
                                            mask = chunk.stack().str.contains('EVENTO|SINISTRO',
                                                                            case=False, na=False).any(level=0)

                                        df_filtrado = chunk[mask].copy()

                                        if not df_filtrado.empty:
                                            # Mapeamento e Normalizacao ---
                                            mapeamento = {
                                                'REG_ANS': 'CNPJ',  # REG_ANS e o identificador nesses arquivos
                                                'NR_CNPJ': 'CNPJ',
                                                'CNPJ_OPERADORA': 'CNPJ',
                                                'VL_SALDO_FINAL': 'VALORDESPESAS',
                                                'VL_EVENTO': 'VALORDESPESAS',
                                                'NM_RAZAO_SOCIAL': 'RAZAOSOCIAL'
                                            }
                                            df_filtrado.rename(
                                                columns=mapeamento, inplace=True)

                                            # Metadados
                                            periodo = os.path.basename(
                                                zip_path).replace(".zip", "")
                                            df_filtrado['TRIMESTRE'] = periodo[0] if 'T' in periodo else "N/A"
                                            df_filtrado['ANO'] = periodo[-4:] if len(
                                                periodo) >= 4 else "N/A"
                                        
                                            # Se RAZAOSOCIAL nao existir no arquivo, criamos como N/A para consolidar
                                            if 'RAZAOSOCIAL' not in df_filtrado.columns:
                                                df_filtrado['RAZAOSOCIAL'] = "NAO IDENTIFICADA"

                                            # Garantir colunas minimas para o CSV final
                                            cols_finais = [
                                                'CNPJ', 'RAZAOSOCIAL', 'TRIMESTRE', 'ANO', 'VALORDESPESAS']
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
