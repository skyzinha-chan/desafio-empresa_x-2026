-- Criação do Schema e Tabelas
-- Compatível com PostgreSQL e MySQL

-- 1. Tabela Dimensão: Operadoras
CREATE TABLE IF NOT EXISTS operadoras (
    registro_ans VARCHAR(10),
    cnpj VARCHAR(14) PRIMARY KEY,
    razao_social VARCHAR(255),
    nome_fantasia VARCHAR(255),
    modalidade VARCHAR(100),
    logradouro VARCHAR(255),
    numero VARCHAR(50),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf VARCHAR(50),
    cep VARCHAR(20),
    telefone VARCHAR(50),
    email VARCHAR(150),
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ops_razao ON operadoras(razao_social);
CREATE INDEX IF NOT EXISTS idx_ops_uf ON operadoras(uf);

-- 2. Tabela Fato: Despesas Financeiras
CREATE TABLE IF NOT EXISTS despesas (
    id SERIAL PRIMARY KEY, -- Use AUTO_INCREMENT no MySQL
    cnpj_operadora VARCHAR(14),
    ano INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    data_evento DATE,
    cd_conta_contabil VARCHAR(50),
    descricao VARCHAR(255),
    valor_despesa DECIMAL(18, 2), -- DECIMAL evita erros de arredondamento de moeda
    data_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_operadora FOREIGN KEY (cnpj_operadora) REFERENCES operadoras(cnpj)
);

CREATE INDEX IF NOT EXISTS idx_despesas_periodo ON despesas(ano, trimestre);
CREATE INDEX IF NOT EXISTS idx_despesas_valor ON despesas(valor_despesa);


-- 3. Tabela de Agregados (Solicitada no Item 3.2)
-- Para performance da API de dashboard (Query 2 e 4.2.3)
CREATE TABLE IF NOT EXISTS despesas_agregadas (
    id SERIAL PRIMARY KEY,
    razao_social VARCHAR(255),
    uf VARCHAR(50),
    total_despesas DECIMAL(18, 2),
    media_trimestral DECIMAL(18, 2),
    desvio_padrao DECIMAL(18, 2),
    data_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_agregados_uf ON despesas_agregadas(uf);