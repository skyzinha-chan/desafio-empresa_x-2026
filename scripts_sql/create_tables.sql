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
    uf CHAR(2),
    cep VARCHAR(20),
    telefone VARCHAR(50),
    email VARCHAR(150),
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ops_razao ON operadoras(razao_social);
CREATE INDEX idx_ops_uf ON operadoras(uf);

-- 2. Tabela Fato: Despesas Financeiras
CREATE TABLE IF NOT EXISTS despesas (
    id SERIAL PRIMARY KEY, -- Use AUTO_INCREMENT no MySQL
    cnpj_operadora VARCHAR(14),
    ano INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    valor_despesa DECIMAL(18, 2), -- DECIMAL evita erros de arredondamento de moeda
    data_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_operadora FOREIGN KEY (cnpj_operadora) REFERENCES operadoras(cnpj)
);

CREATE INDEX idx_despesas_periodo ON despesas(ano, trimestre);
CREATE INDEX idx_despesas_valor ON despesas(valor_despesa);


-- 3. Tabela de Agregados (Opcional - Data Mart)
-- Para performance da API de dashboard (Query 2 e 4.2.3)
CREATE TABLE IF NOT EXISTS despesas_agregadas_uf (
    uf VARCHAR(2),
    ano INTEGER,
    total_despesas DECIMAL(18, 2),
    media_por_operadora DECIMAL(18, 2),
    PRIMARY KEY (uf, ano)
);