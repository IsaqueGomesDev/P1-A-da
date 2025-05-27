from flask import Flask, request, redirect, render_template, url_for
import mysql.connector

app = Flask(__name__)

# Conexão com banco
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="#Thay10121926",
        database="restaurante"
    )

# ----------------------------
# Funções
# ----------------------------
def listar_cardapio():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cardapio")
    data = cursor.fetchall()
    conn.close()
    return data

def adicionar_item(nome, preco, descricao, categoria, ingredientes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cardapio (nome, preco, descricao, categoria, ingredientes)
        VALUES (%s, %s, %s, %s, %s)
    """, (nome, preco, descricao, categoria, ingredientes))
    conn.commit()
    conn.close()

def excluir_item_cardapio(id_item):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cardapio WHERE id = %s", (id_item,))
        conn.commit()
    except mysql.connector.errors.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def listar_mesas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM mesa")
    data = cursor.fetchall()
    conn.close()
    return data

def adicionar_mesa(numero):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mesa (numero) VALUES (%s)", (numero,))
    conn.commit()
    conn.close()

def atualizar_status_mesa(id_mesa, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE mesa SET ocupada = %s WHERE id = %s", (status, id_mesa))
    conn.commit()
    conn.close()

def remover_mesa(id_mesa):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM mesa WHERE id = %s", (id_mesa,))
        conn.commit()
    except mysql.connector.errors.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def listar_pedidos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, m.numero AS mesa, c.nome AS item, p.quantidade, p.status, p.observacoes
        FROM pedido p
        JOIN mesa m ON p.id_mesa = m.id
        JOIN cardapio c ON p.id_cardapio = c.id
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def criar_pedido(id_mesa, id_cardapio, quantidade, observacoes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pedido (id_mesa, id_cardapio, quantidade, observacoes)
        VALUES (%s, %s, %s, %s)
    """, (id_mesa, id_cardapio, quantidade, observacoes))
    conn.commit()
    conn.close()

# ---------------------------------
# Rotas
# ---------------------------------

@app.route('/')
def index():
    return render_template('tela_inicial.html')

@app.route('/cadastro', methods = ['GET','POST'])
def cadastro():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        email = request.form.get('nome')
        senha = request.form.get('senha')
        usuario = request.form.get('usuario')
        cpf = request.form.get('cpf')
    
        cursor.execute("INSERT INTO usuario(email, senha, usuario, cpf) VALUES (%s, %s, %s, %s)", (email, senha, usuario, cpf,))
    conn.close()
    return render_template('cadastro_cliente.html')

@app.route('/login/cliente', methods=['GET', 'POST'])
def login_cliente():
    if request.method == 'POST':
        email = request.form.get('nome')
        senha = request.form.get('senha')

        if email == "admin" and senha == "adm123":
            return redirect(url_for('inicio_admin'))

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT email, senha FROM usuario WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario and usuario['senha'] == senha:
            return redirect(url_for('inicio_cliente'))

    return render_template('login_cliente.html')

@app.route('/inicio/admin')
def inicio_admin():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM mesa")    
    mesas = cursor.fetchall()

    cursor.execute("SELECT * FROM mesa WHERE ocupada = 'disponivel'")
    disponiveis = cursor.fetchall()
    
    conn.close()
    return render_template('admin.html', mesas=mesas, disponiveis=disponiveis)

@app.route('/inicio/cliente')
def inicio_cliente():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM mesa")
    mesas = cursor.fetchall()

    cursor.execute("SELECT * FROM mesa WHERE ocupada = 'disponivel'")
    disponiveis = cursor.fetchall()
    
    conn.close()
    return render_template('cliente.html', mesas=mesas, disponiveis=disponiveis)

@app.route('/login/funcionario', methods=['GET', 'POST'])
def login_funcionario():
    if request.method == 'POST':
        email = request.form.get('nome')
        senha = request.form.get('senha')

        if email == "admin" and senha == "adm123":
            return redirect(url_for('inicio_admin'))

    return render_template('login.html')

@app.route('/cardapio', methods=['GET', 'POST'])
def cardapio_listar():
    cardapio = listar_cardapio()
    return render_template('cardapio.html', cardapio=cardapio)

@app.route('/cardapio/admin', methods=['GET', 'POST'])
def cardapio_admin():
    cardapio = listar_cardapio()
    return render_template('cardapio.html', cardapio=cardapio)

@app.route('/adicionar/cardapio', methods = ['GET', 'POST'])
def adicionar_cardapio():
    if request.method == 'POST':
        adicionar_item(
            request.form['nome'],
            float(request.form['preco']),
            request.form['descricao'],
            request.form['categoria'],
            request.form['ingredientes']
        )

    return render_template('adicionar_cardapio.html', cardapio=listar_cardapio())

@app.route('/excluir_item/<int:id>', methods=['POST'], )
def excluir_item(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('DELETE FROM cardapio WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('cardapio_listar'))

'''

Em analise!!!!
@app.route('/pedidos', methods=['GET', 'POST'])
def pedidos():
    if request.method == 'POST':
        criar_pedido(
            request.form['id_mesa'],
            request.form['id_cardapio'],
            request.form['quantidade'],
            request.form['observacoes']
        )
    return render_template('pedidos.html', pedidos=listar_pedidos(), mesas=listar_mesas(), cardapio=listar_cardapio())
'''
# ----------------------------
# Executar servidor
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)
