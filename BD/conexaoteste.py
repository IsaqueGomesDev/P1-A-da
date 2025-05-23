import os
import sqlite3


def get_db_connection():
  if not os.path.exists('database'):
    os.makedirs('database')
  if not os.path.exists('database/sqlite.db'):
    conn = sqlite3.connect('database/sqlite.db')
    create_tables(conn)
  else:
    conn = sqlite3.connect('database/sqlite.db')
    conn.row_factory = sqlite3.Row
    create_tables(conn)
  return conn


def create_tables(conn):
  conn.execute('''
      CREATE TABLE IF NOT EXISTS categoria(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_da_categoria TEXT NOT NULL
      )
  ''')
  
  conn.execute('''
      CREATE TABLE IF NOT EXISTS museu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        img BLOB,
        id_categoria INTEGER,
        FOREIGN KEY (id_categoria) REFERENCES categoria(id)
      )
  ''')

  inserir(conn)
  conn.commit()


def inserir(conn):
  categorias = conn.execute('SELECT * FROM museu').fetchall()
  info = conn.execute('SELECT * FROM categoria').fetchall()
  if not categorias:
    conn.execute('''
      INSERT INTO museu (nome, descricao)
      values ("creme de avelã", "avelã")
    ''')
    
  if not info:
    conn.execute('''
      INSERT INTO categoria (nome_da_categoria)
      values ("processadores")
    ''')
  
  
