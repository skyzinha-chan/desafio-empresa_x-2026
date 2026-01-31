import zipfile
import os

# Ajuste para subir um nivel e achar a pasta data
zip_path = os.path.join("..", "data", "1T2025.zip")

print("--- Iniciando inspecao de: " + zip_path + " ---")

if os.path.exists(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            print("Arquivos encontrados:")
            for name in z.namelist():
                print(" - " + name)
    except Exception as e:
        print("Erro ao abrir o ZIP: " + str(e))
else:
    print("Arquivo nao encontrado em: " + os.path.abspath(zip_path))
