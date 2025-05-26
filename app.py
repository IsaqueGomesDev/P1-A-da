from flask import Flask, request, redirect, render_template_string
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
# Funções Cardápio
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

# ----------------------------
# Funções Mesas
# ----------------------------
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

# ----------------------------
# Funções Pedidos
# ----------------------------
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
    return render_template_string('tela_inicial.html')

@app.route('/login/cliente')
def login_cliente():
    conn = get_connection()

    email = request.form.get('nome')
    senha = request.form.get('senha')

    cursor = conn.cursor(dictionary=True)

    email_definitivo = cursor.execute("SELECT email FROM usuario WHERE email = ?", (email, ))
    senha_definitiva = cursor.execute("SELECT senha FROM usuario WHERE email = ?", (email, ))

    data = cursor.fetchall()
    conn.close()

    if email =="admin" and senha == "adm123":
        redirect(url_for('inicio_admin'))
    
    elif email_definitivo is not None and senha_definitiva is not None:
        if email == email_definitivo and senha==senha_definitiva:
            redirect(url_for('inicio_cliente'))
    return render_template_string('login_cliente.html', data)

@app.route('/inicio/admin')
def inicio_admin():
    return render_template_string('admin.html')

@app.route('/inicio/cliente')
def inicio_cliente():
    return render_template_string('cliente.html')

@app.route('/login/funcionario')
def login_funcionario():
    email = request.form.get('nome')
    senha = request.form.get('senha')

    if email =="admin" and senha == "adm123":
        redirect(url_for('inicio_admin'))

    return render_template_string('login.html')

@app.route('/cardapio', methods=['GET', 'POST'])
def cardapio():
    if request.method == 'POST':
        adicionar_item(
            request.form['nome'],
            float(request.form['preco']),
            request.form['descricao'],
            request.form['categoria'],
            request.form['ingredientes']
        )
    return render_template_string('cardapio_html', cardapio=listar_cardapio())

@app.route('/excluir_item', methods=['POST'])
def excluir_item():
    id_item = request.form['id']
    excluir_item_cardapio(id_item)
    return redirect('/cardapio')

@app.route('/mesas', methods=['GET'])
def mesas():
    return render_template_string(mesas_html, mesas=listar_mesas())

@app.route('/adicionar_mesa', methods=['POST'])
def adicionar_mesa_route():
    numero = request.form['numero']
    adicionar_mesa(numero)
    return redirect('/mesas')

@app.route('/atualizar_mesa', methods=['POST'])
def atualizar_mesa():
    atualizar_status_mesa(request.form['id'], request.form['status'] == '1')
    return redirect('/mesas')

@app.route('/remover_mesa', methods=['POST'])
def remover_mesa_route():
    remover_mesa(request.form['id'])
    return redirect('/mesas')

@app.route('/pedidos', methods=['GET', 'POST'])
def pedidos():
    if request.method == 'POST':
        criar_pedido(
            request.form['id_mesa'],
            request.form['id_cardapio'],
            request.form['quantidade'],
            request.form['observacoes']
        )
    return render_template_string(pedidos_html, pedidos=listar_pedidos(), mesas=listar_mesas(), cardapio=listar_cardapio())

# ----------------------------
# Executar servidor
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)
