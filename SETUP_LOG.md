# 📋 Guia de Setup: Automação de Estrutura

## Passo 1: Criação de Pastas e Arquivos Base (Em Massa)
Abra o seu terminal na raiz da pasta projeto e execute este bloco único:

```bash
# 1. Criar toda a estrutura de pastas do Backend e Frontend
mkdir -p backend/app/api/routes backend/app/api/controllers backend/app/api/middlewares \
         backend/app/services backend/app/models backend/app/schemas backend/app/core \
         frontend/src/components frontend/src/services scripts_sql data

# 2. Criar arquivos __init__.py para transformar as pastas em módulos Python
touch backend/app/__init__.py backend/app/api/__init__.py \
      backend/app/api/routes/__init__.py backend/app/api/controllers/__init__.py \
      backend/app/api/middlewares/__init__.py backend/app/services/__init__.py \
      backend/app/models/__init__.py backend/app/schemas/__init__.py \
      backend/app/core/__init__.py

# 3. Criar arquivos de configuração na raiz e no backend
touch .gitignore .env.example Dockerfile docker-compose.yml \
      backend/main.py backend/.env backend/requirements.txt \
      data/.gitkeep

```

## Passo 2: Preenchimento do .gitignore
Copie e cole este comando para preencher o arquivo automaticamente:
```bash
cat <<EOT >> .gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Ambientes Virtuais
venv/
.venv/
env/

# Configurações e Segredos
.env
.vscode/
.idea/

# CSV/Data (Muito importante pelo volume de dados)
data/*.csv
data/*.zip
data/*.xlsx
data/*.txt
!data/.gitkeep

# Node (Frontend)
node_modules/
dist/
*.log

# Docker/OS
.DS_Store
Thumbs.db
EOT
```
## Passo 3: Preenchimento do .env.example
Configure o modelo para o avaliador:
```bash
cat <<EOT >> .env.example
# Configurações da API
PROJECT_NAME="EMPRESA_X - Health Analytics"
VERSION="1.0.0"
API_PORT=8000

# Configurações do Banco de Dados
# Exemplo: postgresql://usuario:senha@localhost:5432/nome_do_banco
DATABASE_URL=postgresql://user:password@localhost:5432/empresa_x_db

# Configurações do ETL
ANS_DATA_SOURCE_URL=https://dadosabertos.ans.gov.br/
EOT

```

## Passo 4: Preenchimento do requirements.txt
Adicione as bibliotecas essenciais para o desafio:

```bash
cat <<EOT >> backend/requirements.txt
# --- Framework Web & Servidor ---
fastapi>=0.115.0        # Versão mais atual para compatibilidade 3.13 Framework moderno para construção de APIs rápidas
uvicorn[standard]>=0.30.0       # Servidor ASGI de alta performance para rodar o FastAPI

# --- Processamento de Dados & ETL ---
pandas>=2.2.2          # Manipulação e análise de dados (essencial para os CSVs da ANS)
requests>=2.32.0        # Realização de requisições HTTP (para baixar os ZIPs da API)
openpyxl>=3.1.5        # Suporte para leitura/escrita de arquivos Excel (.xlsx)

# --- Banco de Dados & ORM ---
sqlalchemy>=2.0.30     # Toolkit SQL e ORM para mapeamento de tabelas
psycopg2-binary>=2.9.9  # Driver de conexão para bancos de dados PostgreSQL

# --- Validação & Configurações ---
pydantic>=2.9.0         # Validação de dados e definição de schemas (Data Integrity)
pydantic-settings>=2.5.0 # Gestão de variáveis de ambiente integrada ao Pydantic
python-dotenv>=1.0.1    # Carregamento de variáveis de ambiente a partir do arquivo .env
EOT
```

## Passo 5: Inicialização do Git e Primeiro Commit
Agora que a "casa" está organizada, inicie o versionamento:

```bash
# Iniciar o repositório
git init
```
1. Commit da Estrutura de Pastas e Configurações Base
```bash
# Adicionar os arquivos
git add .gitignore .env.example Dockerfile docker-compose.yml backend/requirements.txt data/.gitkeep
```

```bash
# Criar o primeiro marco do projeto
git commit -m "🎉 chore(setup): infraestrutura inicial e configurações de ambiente

- Criação da árvore de diretórios seguindo Clean Architecture (api, services, models).
- Configuração do arquivo .gitignore para proteção de dados sensíveis e binários.
- Definição do .env.example para padronização das variáveis de ambiente.
- Adição do requirements.txt com dependências comentadas para ETL e API.
- Configuração de Dockerfile e docker-compose para orquestração da stack."
```

2. Commit dos Módulos Python (Arquivos __init__.py)
```bash
git add "**/__init__.py"
git commit -m "🏗️ chore(arch): inicialização dos pacotes pythonicos

- Adição de arquivos __init__.py em todas as subpastas do backend.
- Garantia de que os diretórios app, api, services, models e core sejam reconhecidos como módulos pelo interpretador."
```

3. Commit do README.md e LOG
```bash
git add README.md SETUP_LOG.md
git commit -m "📝 docs(readme): documentação principal e guia de setup

- Finalização do README.md com identidade visual, arquitetura e trade-offs.
- Adição do SETUP_LOG.md para rastreio do histórico de inicialização.
- Inclusão de diagramas Mermaid para visualização do fluxo de dados."
```

## Passo 6: Inicialização e Configuração do Frontend (Vue.js)

Com o backend estruturado, execute estes comandos para configurar a interface moderna com Vue 3, Vite e Tailwind CSS:

```bash
# 1. Criar o scaffold do projeto usando Vite
npm create vite@latest frontend -- --template vue

# 2. Entrar no diretório e instalar as dependências do ecossistema Vue
cd frontend
npm install

# 3. Instalar bibliotecas de suporte (Comunicação, Gráficos e Ícones)
# Axios: Requisições HTTP
# Chart.js + Vue-Chartjs: Visualização de dados (Item 4.3 do desafio)
# Lucide-vue-next: Biblioteca de ícones modernos
npm install axios chart.js vue-chartjs lucide-vue-next

# 4. Instalar Framework de Estilização (Tailwind CSS)
npm install -D tailwindcss postcss autoprefixer

# 5. Inicializar as configurações do Tailwind
npx tailwindcss init -p

npm run dev
```

## Passo 8: Preparação da Entrega Final (Compactação)

Para garantir que o avaliador receba um arquivo leve e organizado, execute o comando de compactação ignorando as pastas de dependências (`node_modules` e `venv`), que devem ser instaladas pelo próprio avaliador.

### No Git Bash ou Linux (Recomendado):
```bash
# Gera o ZIP final ignorando binários pesados e pastas de ambiente
zip -r Teste_Talita_Mendonca.zip . -x "**/node_modules/*" "**/venv/*" "**/.git/*" "**/__pycache__/*" "frontend/dist/*"