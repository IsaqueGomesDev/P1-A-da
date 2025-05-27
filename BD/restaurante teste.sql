-- Recria o banco
DROP DATABASE IF EXISTS restaurante;
CREATE DATABASE restaurante;
USE restaurante;

-- Tabela de Usuários (clientes e funcionários)
CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('cliente', 'funcionario') DEFAULT 'cliente'
);

-- Tabela de Mesas
CREATE TABLE mesa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero INT NOT NULL UNIQUE,
    status ENUM('disponivel', 'ocupada', 'reservada') DEFAULT 'disponivel'
);

-- Tabela de Cardápio (equivalente ao 'prato')
CREATE TABLE cardapio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    ingredientes TEXT,
    preco DECIMAL(10,2) NOT NULL,
    categoria ENUM('entrada', 'prato principal', 'sobremesa', 'bebida') NOT NULL
);

-- Tabela de Pedidos
CREATE TABLE pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_mesa INT NOT NULL,
    id_cardapio INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    status ENUM('em preparo', 'pronto', 'entregue') DEFAULT 'em preparo',
    observacoes TEXT,
    FOREIGN KEY (id_mesa) REFERENCES mesa(id) ON DELETE CASCADE,
    FOREIGN KEY (id_cardapio) REFERENCES cardapio(id)
);

-- Tabela de Reservas Pendentes feitas por usuários
CREATE TABLE reserva_pendente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    id_mesa INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id),
    FOREIGN KEY (id_mesa) REFERENCES mesa(id)
);

-- Tabela de Reservas Confirmadas
CREATE TABLE reserva_definitiva (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva INT NOT NULL,
    data_confirmacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_reserva) REFERENCES reserva_pendente(id) ON DELETE CASCADE
);
