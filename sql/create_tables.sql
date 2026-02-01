CREATE TABLE operadoras (
    registro_ans INT PRIMARY KEY,
    cnpj VARCHAR(20),
    razao_social VARCHAR(255),
    modalidade VARCHAR(100),
    uf CHAR(2)
);

CREATE TABLE demonstracoes_contabeis (
    id SERIAL PRIMARY KEY,
    registro_ans INT,
    ano INT,
    trimestre INT,
    valor_despesa NUMERIC(18,2),
    FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans)
);

CREATE TABLE despesas_agregadas (
    registro_ans INT PRIMARY KEY,
    razao_social VARCHAR(255),
    uf CHAR(2),
    total_despesas NUMERIC(18,2),
    media_trimestral NUMERIC(18,2),
    desvio_padrao NUMERIC(18,2),
    FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans)
);