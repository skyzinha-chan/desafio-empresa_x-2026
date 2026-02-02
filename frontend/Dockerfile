# Usa imagem leve do Node.js 22
FROM node:22-alpine

# Define diretório de trabalho
WORKDIR /frontend

# Copia os arquivos de dependências primeiro (para cache do Docker ser eficiente)
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia o restante do código fonte
COPY . .

# Expõe a porta padrão do Vite
EXPOSE 5173

# Comando para rodar o servidor de desenvolvimento liberando acesso externo (--host)
CMD ["npm", "run", "dev", "--", "--host"]