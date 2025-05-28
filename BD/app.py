from flask import Flask, request, redirect, render_template_string


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

# ----------------------------
# HTML Templates
# ----------------------------
index_html = """
<h1>Restaurante</h1>
<a href="/cardapio">Cardápio</a> |
<a href="/mesas">Mesas</a> |
<a href="/pedidos">Pedidos</a>
"""

# Cardápio
cardapio_html = """
<h1>Cardápio</h1>
<ul>
  {% for item in cardapio %}
    <li>{{ item.nome }} - R$ {{ item.preco }} 
        <form method="post" action="/excluir_item" style="display:inline">
            <input type="hidden" name="id" value="{{ item.id }}">
            <button type="submit">Excluir</button>
        </form>
    </li>
  {% endfor %}
</ul>
<h2>Adicionar Item</h2>
<form method="post" action="/cardapio">
  Nome: <input name="nome"><br>
  Preço: <input name="preco" type="number" step="0.01"><br>
  Descrição: <input name="descricao"><br>
  Categoria: <input name="categoria"><br>
  Ingredientes: <input name="ingredientes"><br>
  <button type="submit">Adicionar</button>
</form>
<a href="/">Voltar</a>
"""

# Mesas
mesas_html = """
<h1>Mesas</h1>
<ul>
  {% for mesa in mesas %}
    <li>
      Mesa {{ mesa.numero }} - {{ 'Ocupada' if mesa.ocupada else 'Livre' }}
      <form method="post" action="/atualizar_mesa" style="display:inline">
        <input type="hidden" name="id" value="{{ mesa.id }}">
        <input type="hidden" name="status" value="{{ '0' if mesa.ocupada else '1' }}">
        <button type="submit">{{ 'Liberar' if mesa.ocupada else 'Ocupar' }}</button>
      </form>
      <form method="post" action="/remover_mesa" style="display:inline">
        <input type="hidden" name="id" value="{{ mesa.id }}">
        <button type="submit">Remover</button>
      </form>
    </li>
  {% endfor %}
</ul>
<h2>Adicionar Mesa</h2>
<form method="post" action="/adicionar_mesa">
  Número da mesa: <input name="numero" type="number"><br>
  <button type="submit">Adicionar</button>
</form>
<a href="/">Voltar</a>
"""

# Pedidos
pedidos_html = """
<h1>Pedidos</h1>
<ul>
  {% for pedido in pedidos %}
    <li>Mesa {{ pedido.mesa }} - {{ pedido.item }} ({{ pedido.quantidade }}) - {{ pedido.status }}<br>Obs: {{ pedido.observacoes }}</li>
  {% endfor %}
</ul>

<h2>Fazer novo pedido</h2>
<form method="post" action="/pedidos">
  Mesa:
  <select name="id_mesa">
    {% for mesa in mesas %}
      <option value="{{ mesa.id }}">Mesa {{ mesa.numero }}</option>
    {% endfor %}
  </select><br>
  Item:
  <select name="id_cardapio">
    {% for item in cardapio %}
      <option value="{{ item.id }}">{{ item.nome }}</option>
    {% endfor %}
  </select><br>
  Quantidade: <input type="number" name="quantidade"><br>
  Observações: <input name="observacoes"><br>
  <button type="submit">Fazer Pedido</button>
</form>
<a href="/">Voltar</a>
"""

# ----------------------------
# Rotas Flask
# ----------------------------
@app.route('/')
def index():
    return render_template_string(index_html)

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
    return render_template_string(cardapio_html, cardapio=listar_cardapio())

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
