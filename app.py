from flask import Flask, request, redirect, render_template, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para usar sessões

# Conexão com banco
def get_connection():
    try:
        return mysql.connector.connect(
            host="127.0.0.1",  
            user="root",
            password="#Thay10121926",
            database="restaurante",
            port=3306  
        )
    except mysql.connector.Error as err:
        print(f"Erro de conexão: {err}")
        raise

# Funções
def listar_cardapio():
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM cardapio")
            data = cursor.fetchall()
    return data

def adicionar_item(nome, preco, descricao, categoria, ingredientes):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cardapio (nome, preco, descricao, categoria, ingredientes)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, preco, descricao, categoria, ingredientes))
            conn.commit()

def excluir_item_cardapio(id_item):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM cardapio WHERE id = %s", (id_item,))
                conn.commit()
            except mysql.connector.errors.IntegrityError:
                return False
    return True

def listar_mesas():
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM mesa")
            data = cursor.fetchall()
    return data

def adicionar_mesa(numero):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO mesa (numero) VALUES (%s)", (numero,))
            conn.commit()

def atualizar_status_mesa(id_mesa, status):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE mesa SET ocupada = %s WHERE id = %s", (status, id_mesa))
            conn.commit()

def excluir_mesa(id_mesa):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM mesa WHERE id = %s", (id_mesa,))
                conn.commit()
            except mysql.connector.errors.IntegrityError:
                return False
    return True

def listar_pedidos():
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT p.id, m.numero AS mesa, c.nome AS item, p.quantidade, p.status, p.observacoes
                FROM pedido p
                JOIN mesa m ON p.id_mesa = m.id
                JOIN cardapio c ON p.id_cardapio = c.id
            """)
            data = cursor.fetchall()
    return data

def adicionar_pedido(id_mesa, id_cardapio, quantidade, observacoes):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO pedido (id_mesa, id_cardapio, quantidade, observacoes)
                VALUES (%s, %s, %s, %s)
            """, (id_mesa, id_cardapio, quantidade, observacoes))
            conn.commit()

# Rotas
@app.route('/')
def index():
    return render_template('tela_inicial.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form.get('nome')
        senha = request.form.get('senha')
        usuario = request.form.get('usuario')
        cpf = request.form.get('cpf')

        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("INSERT INTO usuario(email, senha, usuario, cpf) VALUES (%s, %s, %s, %s)", 
                               (email, senha, usuario, cpf))
                conn.commit()
                return redirect(url_for('login_cliente'))

    return render_template('cadastro_cliente.html')

@app.route('/login/cliente', methods=['GET', 'POST'])
def login_cliente():
    if request.method == 'POST':
        email = request.form.get('nome')
        senha = request.form.get('senha')

        if email == "admin" and senha == "adm123":
            return redirect(url_for('inicio_admin'))

        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id, email, senha FROM usuario WHERE email = %s", (email,))
                usuario = cursor.fetchone()

        if usuario and usuario['senha'] == senha:
            session['usuario_id'] = usuario['id']
            return redirect(url_for('inicio_cliente'))

    return render_template('login_cliente.html')

@app.route('/inicio/admin')
def inicio_admin():
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM mesa")
                mesas = cursor.fetchall()

                cursor.execute("SELECT * FROM mesa WHERE ocupada = 0")
                disponiveis = cursor.fetchall()

                return render_template('admin.html', mesas=mesas, disponiveis=disponiveis)
    except Exception as e:
        return f"Erro ao carregar admin: {e}", 500

@app.route('/inicio/cliente')
def inicio_cliente():
    usuario_id = session.get('usuario_id')

    if not usuario_id:
        return redirect(url_for('login_cliente'))

    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM mesa")
            mesas = cursor.fetchall()

            cursor.execute("SELECT * FROM mesa WHERE ocupada = 0")
            disponiveis = cursor.fetchall()

    return render_template('cliente.html', mesas=mesas, disponiveis=disponiveis)

@app.route('/login/funcionario', methods=['GET', 'POST'])
def login_funcionario():
    if request.method == 'POST':
        email = request.form.get('nome')
        senha = request.form.get('senha')

        if email == "admin" and senha == "adm123":
            return redirect(url_for('inicio_admin'))
        else:
            return render_template('login.html')

    return render_template('login.html')

@app.route('/cardapio', methods=['GET', 'POST'])
def cardapio_listar():
    cardapio = listar_cardapio()
    return render_template('cardapio.html', cardapio=cardapio)

@app.route('/cardapio/admin', methods=['GET', 'POST'])
def cardapio_admin():
    cardapio = listar_cardapio()
    return render_template('cardapio.html', cardapio=cardapio)

@app.route('/adicionar/cardapio', methods=['GET', 'POST'])
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

@app.route('/excluir_item/<int:id>', methods=['POST'])
def excluir_item(id):
    if excluir_item_cardapio(id):
        return redirect(url_for('cardapio_listar'))
    else:
        return "Erro ao excluir item", 400

@app.route('/pedidos', methods=['GET', 'POST'])
def pedidos():
    pedidos = listar_pedidos()
    mesas = listar_mesas()
    cardapio = listar_cardapio()

    return render_template('pedidos.html', pedidos=pedidos, mesas=mesas, cardapio=cardapio)

@app.route('/editar/reserva', methods=['GET', 'POST'])
def editar_reserva():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form.get('cpf')
        usuario_id = session.get('usuario_id')

        if not usuario_id:
            return redirect(url_for('login_cliente'))

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('UPDATE reserva SET nome = %s, cpf = %s WHERE id = %s', (nome, cpf, usuario_id))
                conn.commit()

        return redirect(url_for('index'))  # Redirecionamento ajustável

    return render_template('editar_reserva.html')

@app.route('/sobre/prato')
def sobre_o_prato():
    return render_template('sobre_o_prato.html')

@app.route('/editar/cardapio')
def editar_cardapio():
    return render_template('editar_cardapio.html')

@app.route('/reserva/admin')
def reserva_admin():
    return render_template('reserva.html')

@app.route('/adicionar/reserva')
def adicionar_reserva():
    return render_template('adicionar_reserva.html')

@app.route('/pedido/admin')
def pedido_admin():
    return render_template('pedido.html')

@app.route('/adiciona/pedido')
def adicionar_pedido():
    if request.method == 'POST':
        adicionar_pedido(
            request.form['id_mesa'],
            request.form['id_cardapio'],
            request.form['quantidade'],
            request.form['observacoes']
        )
    return render_template('adicionar_pedido.html')

@app.route('/editar/pedido')
def editar_pedido():
    return render_template('editar_pedido.html')

@app.route('/solicitacoes/reserva')
def solicitacoes():
    return render_template('solicitacoes.html')

@app.route('/pedido/cliente')
def pedido_cliente():
    return render_template('pedido_cliente.html')

@app.route('/cardapio/cliente')
def cardapio_cliente():
    return render_template('cardapio_cliente.html')


# Executar servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
