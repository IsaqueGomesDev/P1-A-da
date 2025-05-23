
DROP DATABASE IF EXISTS restaurante;
CREATE DATABASE restaurante;
USE restaurante;


CREATE TABLE cardapio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    preco DECIMAL(10,2),
    descricao VARCHAR(100),
    categoria VARCHAR(100),
	ingredientes VARCHAR(100)
);


CREATE TABLE mesa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero INT,
    ocupada BOOLEAN DEFAULT FALSE
);

CREATE TABLE pedido (
	id INT AUTO_INCREMENT PRIMARY KEY,
    id_mesa INT,
    id_cardapio INT,
    quantidade INT,
    status VARCHAR(20) DEFAULT 'em preparo',
    observacoes TEXT,
    FOREIGN KEY (id_mesa) REFERENCES mesa(id),
    FOREIGN KEY (id_cardapio) REFERENCES cardapio(id)
);
