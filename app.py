from flask import Flask, request, render_template, redirect, url_for, jsonify, session, flash
import json
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
DATA_DIR = "data"
app.secret_key = os.environ.get('SECRET_KEY', '123456')

def load_data(filename):
    try:
        caminho = os.path.join(DATA_DIR, filename)
        if not os.path.exists(caminho):
            with open(caminho, 'w') as f:
                json.dump([], f)  # Corrigido para lista
            return []
        
        with open(caminho, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError(f"Arquivo {filename} não contém uma lista válida")
            return data
    except json.JSONDecodeError:
        raise ValueError(f"Arquivo {filename} contém JSON inválido")
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo {filename}: {str(e)}")
    

def save_data(filename, data):
    try:
        with open(os.path.join(DATA_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise Exception(f'Erro ao salvar dados: {str(e)}')

def buscar_item_por_id(items, id):
    return next((item for item in items if item['id'] == id), None)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or session.get('tipo_usuario') != 'admin':
            flash('Acesso negado')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def gerar_id(items):
    if not items:
        return 1
    return max(item.get('id', 0) for item in items) + 1







@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route("/")
def tela_inicial():
    return render_template('tela_inicial.html')

@app.route('/admin', methods=['GET'])
@login_required
@admin_required
def admin():
    try:
        return render_template('admin.html')
    except Exception as e:
        flash(f'Erro ao carregar página: {str(e)}')
        return redirect(url_for('login'))

@app.route('/login/cliente', methods=['GET', 'POST'])
def login_cliente():
    if request.method == 'POST':
        try:
            # Verifica se os campos foram preenchidos
            if not request.form.get('email') or not request.form.get('senha'):
                flash('Por favor, preencha todos os campos', 'error')
                return redirect(url_for('login_cliente'))

            # Carrega os clientes
            clientes = load_data('cliente.json')
            
            # Procura o cliente pelo email
            cliente = next((c for c in clientes if c['email'].lower() == request.form['email'].lower()), None)
            
            if not cliente:
                flash('Email não encontrado', 'error')
                return redirect(url_for('login_cliente'))
            
            # Verifica a senha
            if check_password_hash(cliente['senha'], request.form['senha']):
                # Login bem-sucedido
                session['usuario_id'] = cliente['id']
                session['tipo_usuario'] = 'cliente'
                session['nome_usuario'] = cliente['nome']
                flash(f'Bem-vindo(a), {cliente["nome"]}!', 'success')
                return redirect(url_for('inicio_cliente'))
            else:
                flash('Senha incorreta', 'error')
                return redirect(url_for('login_cliente'))
                
        except Exception as e:
            flash(f'Erro ao fazer login: {str(e)}', 'error')
            return redirect(url_for('login_cliente'))
            
    return render_template('login_cliente.html')

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        try:
            admins = load_data('admin.json')
            admin = next((a for a in admins if a['email'] == request.form['email']), None)
            if admin and check_password_hash(admin['senha'], request.form['senha']):
                session['usuario_id'] = admin['id']
                session['tipo_usuario'] = 'admin'
                return redirect(url_for('admin'))
            flash('Email ou senha inválidos')
            return redirect(url_for('login_admin'))
        except Exception as e:
            flash(f'Erro ao fazer login: {str(e)}')
            return redirect(url_for('login_admin'))
    return render_template('login.html')

@app.route('/cadastro/cliente', methods=['GET', 'POST'])
def cadastro_cliente():
    if request.method == 'POST':
        campos_obrigatorios = ['nome', 'email', 'senha', 'usuario', 'cpf']
        if not all(k in request.form and request.form[k].strip() != '' for k in campos_obrigatorios):
            flash('Todos os campos são obrigatórios', 'error')
            return redirect(url_for('cadastro_cliente'))
        
        try:
            clientes = load_data('cliente.json')
            if any(c['email'] == request.form['email'] for c in clientes):
                flash('Este email já está cadastrado. Por favor, use outro email.', 'error')
                return redirect(url_for('cadastro_cliente'))
            
            novo_cliente = {
                "id": gerar_id(clientes),
                "nome": request.form['nome'],
                "usuario": request.form['usuario'],
                "cpf": request.form['cpf'],
                "email": request.form['email'],
                "senha": generate_password_hash(request.form['senha'])
            }
            clientes.append(novo_cliente)
            save_data('cliente.json', clientes)

            session['usuario_id'] = novo_cliente['id']
            session['tipo_usuario'] = 'cliente'
            
            flash('Cadastro realizado com sucesso! Bem-vindo ao sistema.', 'success')
            return redirect(url_for('inicio_cliente'))
        except Exception as e:
            flash(f'Erro ao realizar cadastro: {str(e)}', 'error')
            return redirect(url_for('cadastro_cliente'))
    
    return render_template('cadastro_cliente.html')

# ---------- CRUD CARDÁPIO ----------
@app.route('/cardapio', methods=['GET'])
def listar_cardapio():
    cardapio = load_data('cardapio.json')
    return render_template('cardapio.html', cardapio=cardapio)

@app.route("/adicionar/cardapio")
def adicionar_cardapio_template():
    return render_template("adicionar_cardapio.html")

@app.route("/adicionar_cardapio", methods=["POST"])
def adicionar_cardapio():
    cardapio = load_data("cardapio.json")
    item = {k: v.upper() if isinstance(v, str) else v for k, v in request.form.to_dict().items()}
    item["id"] = len(cardapio) + 1
    cardapio.append(item)
    save_data("cardapio.json", cardapio)
    return redirect(url_for("listar_cardapio"))

@app.route("/editar/cardapio/<int:item_id>", methods=["GET", "POST"])
def editar_cardapio(item_id):
    cardapio = load_data("cardapio.json")

    if request.method == "POST":
        for item in cardapio:
            if item["id"] == item_id:
                item.update(request.form.to_dict())
                break
        save_data("cardapio.json", cardapio)
        return redirect(url_for("listar_cardapio"))
    else:
        item = next((i for i in cardapio if i["id"] == item_id), None)
        return render_template("editar_cardapio.html", item=item)

@app.route("/excluir/cardapio/<int:item_id>")
def excluir_cardapio(item_id):
    cardapio = load_data("cardapio.json")
    cardapio = [item for item in cardapio if item["id"] != item_id]
    save_data("cardapio.json", cardapio)
    return redirect(url_for("listar_cardapio"))


# ---------- CRUD MESAS ----------
@app.route('/mesas', methods=['GET'])
def listar_mesa():
    mesas = load_data('mesa.json')

    for mesa in mesas:
        status = mesa.get('status', '')
        mesa['status'] = status.upper()[:1]  # ex: "disponivel" → "D"

    return render_template('mesas.html', mesas=mesas)

@app.route("/adicionar/mesa")
def adicionar_mesa_template():
    return render_template("adicionar_mesa.html")

@app.route("/adicionar_mesa", methods=["POST"])
def adicionar_mesa():
    mesas = load_data("mesa.json")
    nova = request.form.to_dict()
    nova["id"] = len(mesas) + 1
    mesas.append(nova)
    save_data("mesa.json", mesas)
    return redirect(url_for("listar_mesa"))
    
@app.route("/editar/mesa/<int:mesa_id>", methods=["GET", "POST"])
def editar_mesa(mesa_id):
    lista_mesas = load_data("mesa.json")
    if request.method == "POST":
        for mesa in lista_mesas:
            if mesa["id"] == mesa_id:
                mesa.update(request.form.to_dict())
                break
        save_data("mesa.json", lista_mesas)
        return redirect(url_for("listar_mesa"))
    else:
        mesa = next((i for i in lista_mesas if i["id"] == mesa_id), None)
        return render_template("editar_mesa.html", mesa=mesa)

@app.route("/excluir/mesa/<int:mesa_id>")
def excluir_mesa(mesa_id):
    mesas = load_data("mesa.json")
    mesas = [m for m in mesas if m["id"] != mesa_id]
    save_data("mesa.json", mesas)
    return redirect(url_for("listar_mesa"))


# ---------- CRUD PEDIDOS ----------


@app.route('/pedidos', methods=['GET'])
def listar_pedidos():
    pedidos = load_data('pedido.json')
    return render_template('pedido.html', pedidos=pedidos)

@app.route("/adicionar/pedido")
def adicionar_pedido_template():
    mesas = load_data('mesa.json')
    mesas_ocupadas = [mesa for mesa in mesas if mesa["status"] == "ocupado"]
    return render_template("adicionar_pedido.html", mesas=mesas_ocupadas)

@app.route("/adicionar_pedido", methods=["POST"])
def adicionar_pedido():
    pedidos = load_data("pedido.json")
    novo = request.form.to_dict()
    novo["id"] = len(pedidos) + 1
    pedidos.append(novo)
    save_data("pedido.json", pedidos)
    return redirect(url_for("listar_pedidos"))

@app.route('/pedido/cliente')
def pedido_cliente():
    return render_template('pedido_cliente.html')

#ROTA DE ADICIONAR PEDIDO VINDO DO CLIENTE
@app.route("/adicionar_pedido_cliente", methods=["POST"])
def adicionar_pedido_cliente():
    pedidos = load_data("pedido.json")
    novo_pedido = {
        "id": len(pedidos) + 1,
        "num_mesa": request.form["num_mesa"],
        "prato": request.form["prato"],
        "status_pedido": "Em preparo"
    }
    pedidos.append(novo_pedido)
    save_data("pedido.json", pedidos)

    return redirect(url_for("cardapio_cliente", mensagem="Pedido realizadoo!"))

@app.route("/editar/pedido/<int:pedido_id>", methods=["GET", "POST"])
def editar_pedido(pedido_id):
    pedidos = load_data("pedido.json")
    mesas = load_data('mesa.json')
    mesas_ocupadas = [mesa for mesa in mesas if mesa["status"] == "ocupado"]

    if request.method == "POST":
        for p in pedidos:
            if p["id"] == pedido_id:
                p.update(request.form.to_dict())
                break
        save_data("pedido.json", pedidos)
        return redirect(url_for("listar_pedidos"))
    else:
        novo = next((i for i in pedidos if i["id"] == pedido_id), None)
        return render_template("editar_pedido.html", novo=novo, mesas=mesas_ocupadas)


@app.route("/excluir/pedido/<int:pedido_id>")
def excluir_pedido(pedido_id):
    pedidos = load_data("pedido.json")
    pedidos = [p for p in pedidos if p["id"] != pedido_id]
    save_data("pedido.json", pedidos)
    return redirect(url_for("listar_pedidos"))


# ---------- CRUD RESERVAS ----------


@app.route('/reserva/admin', methods=['GET'])
def listar_reserva():
    reserva = load_data('reserva.json')
    mesas = load_data('mesa.json')
    return render_template('reserva.html', reserva=reserva, mesas=mesas)

@app.route("/adicionar/reserva")
def adicionar_reserva_template():
    mesas = load_data("mesa.json")
    mesas_disponiveis = [mesa for mesa in mesas if mesa["status"] == "disponivel"]
    return render_template("adicionar_reserva.html", mesas=mesas_disponiveis)

@app.route("/adicionar_reserva", methods=["POST"])
def adicionar_reserva():
    reservas = load_data("reserva.json")
    nova_reserva = request.form.to_dict()
    nova_reserva["id"] = len(reservas) + 1
    nova_reserva["id_mesa"] = int(nova_reserva["id_mesa"])  # converter pra int
    reservas.append(nova_reserva)
    save_data("reserva.json", reservas)

    # Atualizar o status da mesa para "ocupado"
    mesas = load_data("mesa.json")
    for mesa in mesas:
        if mesa["id"] == nova_reserva["id_mesa"]:
            mesa["status"] = "ocupado"
            break
    save_data("mesa.json", mesas)

    return redirect(url_for("listar_reserva"))

@app.route("/adicionar_reserva/cliente", methods=["POST"])
def adicionar_reserva_cliente():
    reservas = load_data("reserva.json")
    nova_reserva = request.form.to_dict()
    nova_reserva["id"] = len(reservas) + 1
    nova_reserva["id_mesa"] = int(nova_reserva["id_mesa"])  # converter pra int
    reservas.append(nova_reserva)
    save_data("reserva.json", reservas)

    # Atualizar o status da mesa para "ocupado"
    mesas = load_data("mesa.json")
    for mesa in mesas:
        if mesa["id"] == nova_reserva["id_mesa"]:
            mesa["status"] = "ocupado"
            break
    save_data("mesa.json", mesas)

    return redirect(url_for("inicio_cliente"))

@app.route("/editar/reserva/<int:nova_reserva_id>", methods=["GET", "POST"])
def editar_reserva(nova_reserva_id):
    reservas = load_data("reserva.json")
    mesas = load_data("mesa.json")
    mesas_disponiveis = [mesa for mesa in mesas if mesa["status"] == "disponivel"]

    # Para a edição, queremos incluir a mesa atual da reserva mesmo que não esteja "disponível"
    reserva_atual = next((r for r in reservas if r["id"] == nova_reserva_id), None)
    if reserva_atual:
        # incluir mesa atual na lista de opções para editar
        mesa_reserva = next((m for m in mesas if m["id"] == reserva_atual.get("id_mesa")), None)
        if mesa_reserva and mesa_reserva not in mesas_disponiveis:
            mesas_disponiveis.append(mesa_reserva)

    if request.method == "POST":
        for r in reservas:
            if r["id"] == nova_reserva_id:
                # Antes de atualizar, liberar mesa antiga
                mesas = load_data("mesa.json")
                for mesa in mesas:
                    if mesa["id"] == r.get("id_mesa"):
                        mesa["status"] = "disponivel"
                        break
                save_data("mesa.json", mesas)

                # Atualiza a reserva com os novos dados
                r.update(request.form.to_dict())
                r["id_mesa"] = int(r["id_mesa"])

                # Marca a nova mesa como ocupada
                for mesa in mesas:
                    if mesa["id"] == r["id_mesa"]:
                        mesa["status"] = "ocupado"
                        break
                save_data("mesa.json", mesas)
                break
        save_data("reserva.json", reservas)
        return redirect(url_for("listar_reserva"))

    else:
        return render_template("editar_reserva.html", nova_reserva=reserva_atual, mesas=mesas_disponiveis)

@app.route("/excluir/reserva/<int:reserva_id>")
def excluir_reserva(reserva_id):
    reservas = load_data("reserva.json")
    mesas = load_data("mesa.json")
    reserva_a_excluir = next((r for r in reservas if r["id"] == reserva_id), None)

    if reserva_a_excluir:
        # Liberar a mesa da reserva excluída
        for mesa in mesas:
            if mesa["id"] == reserva_a_excluir.get("id_mesa"):
                mesa["status"] = "disponivel"
                break
        save_data("mesa.json", mesas)

    reservas = [r for r in reservas if r["id"] != reserva_id]
    save_data("reserva.json", reservas)
    return redirect(url_for("listar_reserva"))



@app.route('/cardapio/cliente', methods=['GET'])
def cardapio_cliente():
   cardapio = load_data('cardapio.json')
   mesas = load_data('mesa.json')
   mesas_ocupadas = [mesa for mesa in mesas if mesa["status"] == "ocupado"]
   return render_template('cardapio_cliente.html', cardapio=cardapio, mesas = mesas_ocupadas)

@app.route('/inicio/cliente', methods=["GET", "POST"])
def inicio_cliente():
    mesas_total = load_data('mesa.json')
    mesas = load_data('mesa.json')
    mesas_ocupadas = [mesa for mesa in mesas if mesa["status"] == "ocupado"]

    num_mesa = None
    pedidos_acompanhamento = []

    if request.method == "POST":
        num_mesa = request.form.get('num_mesa')  # número da mesa vindo do formulário
        pedidos = load_data("pedido.json")
        if num_mesa:
            pedidos_acompanhamento = [
                pedido for pedido in pedidos if str(pedido["num_mesa"]) == str(num_mesa)
            ]

    return render_template(
        'inicio_cliente.html',
        mesas_total=mesas_total,
        pedidos=pedidos_acompanhamento,
        mesas=mesas_ocupadas,
        mesa_selecionada=num_mesa
    )

if __name__ == '__main__':
    app.run(debug=True)
