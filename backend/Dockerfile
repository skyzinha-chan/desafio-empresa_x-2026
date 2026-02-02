# Usa uma imagem leve do Python 3.10
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /backend

# Variáveis de ambiente para o Python não gerar arquivos .pyc e logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala as dependências do sistema necessárias (para SQLite e compilação se precisar)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do backend para dentro do container
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]