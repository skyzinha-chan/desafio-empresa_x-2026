import os
import sys

# Adiciona o diretório raiz ao path para garantir que o Python encontre os módulos
# Isso ajuda a evitar erros de "Module not found" dependendo de onde você roda o script
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../../")))

try:
    # Tenta importar como módulo do pacote app
    from app.services.step1_etl import Step1ETL
    from app.services.step2_transformation import Step2Transformation
    from app.services.step3_db_ingestion import Step3DBIngestion
except ImportError:
    # Fallback para importação direta se estiver rodando scripts soltos (menos comum, mas seguro)
    from step1_etl import Step1ETL
    from step2_transformation import Step2Transformation
    from step3_db_ingestion import Step3DBIngestion



class ANSService:
    """
    Orquestrador Central do Pipeline.
    Responsável por executar a Etapa 1 e, se bem-sucedida, a Etapa 2.
    """

    @classmethod
    def executar_pipeline_completo(cls):
        print("========================================================")
        print("🏁 INICIANDO PIPELINE DE DADOS DA EMPRESA_X")
        print("========================================================\n")

        # --- ETAPA 1: ETL (Extração e Consolidação Bruta) ---
        try:
            print(">>> EXECUTANDO ETAPA 1: Integração ANS e Consolidação")
            Step1ETL.execute()

            # Verificação de segurança: Se o arquivo não foi gerado, não adianta ir para a etapa 2
            arquivo_consolidado = os.path.join(
                Step1ETL.DATA_DIR, "consolidado_despesas.csv")
            if not os.path.exists(arquivo_consolidado):
                print("❌ Erro Crítico: O arquivo consolidado não foi gerado na Etapa 1.")
                return

        except Exception as e:
            print(f"❌ Falha fatal na Etapa 1: {e}")
            return  # Interrompe tudo

        print("\n--------------------------------------------------------\n")

        # --- ETAPA 2: Transformação (Enriquecimento e Agregação) ---
        try:
            print(">>> EXECUTANDO ETAPA 2: Transformação e Enriquecimento (CADOP)")
            Step2Transformation.execute()
        except Exception as e:
            print(f"❌ Falha fatal na Etapa 2: {e}")
            return

        print("\n--------------------------------------------------------\n")
        # --- ETAPA 3: Ingestão no Banco de Dados ---
        try:
            print(">>> EXECUTANDO ETAPA 3: Ingestão no Banco de Dados")
            Step3DBIngestion.execute()
        except Exception as e:
            print(f"❌ Falha fatal na Etapa 3: {e}")
            return


        print("\n========================================================")
        print("✨ PIPELINE FINALIZADO COM SUCESSO! ✨")
        print("========================================================")


if __name__ == "__main__":
    ANSService.executar_pipeline_completo()
