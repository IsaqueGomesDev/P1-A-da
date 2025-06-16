from flask import Flask, request, render_template, redirect, url_for
import json, os

app = Flask(__name__)
DATA_DIR = "data"

def load_data(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f)
    with open(path, "r") as f:
        return json.load(f)

def save_data(filename, data):
    with open(os.path.join(DATA_DIR, filename), "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def tela_inicial():
    return render_template('tela_inicial.html')

@app.route('/inicio/admin')
def inicio_admin():
    return render_template('admin.html')

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
    item = request.form.to_dict()
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
    return render_template("adicionar_pedido.html")

@app.route("/adicionar_pedido", methods=["POST"])
def adicionar_pedido():
    pedidos = load_data("pedido.json")
    novo = request.form.to_dict()
    novo["id"] = len(pedidos) + 1
    pedidos.append(novo)
    save_data("pedido.json", pedidos)
    return redirect(url_for("listar_pedidos"))

@app.route("/editar/pedido/<int:pedido_id>", methods=["GET", "POST"])
def editar_pedido(pedido_id):
    pedidos = load_data("pedido.json")

    if request.method == "POST":
        for p in pedidos:
            if p["id"] == pedido_id:
                p.update(request.form.to_dict())
                break
        save_data("pedido.json", pedidos)
        return redirect(url_for("listar_pedidos"))
    else:
        novo = next((i for i in pedidos if i["id"] == pedido_id), None)
        return render_template("editar_pedido.html", novo=novo)


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
    return render_template('reserva.html', reserva=reserva)

@app.route("/adicionar/reserva")
def adicionar_reserva_template():
    return render_template("adicionar_reserva.html")

@app.route("/adicionar_reserva", methods=["POST"])
def adicionar_reserva():
    reservas = load_data("reserva.json")
    nova = request.form.to_dict()
    nova["id"] = len(reservas) + 1
    reservas.append(nova)
    save_data("reserva.json", reservas)
    return redirect(url_for("listar_reserva"))

@app.route("/excluir_reserva/<int:reserva_id>")
def excluir_reserva(reserva_id):
    reservas = load_data("reserva.json")
    reservas = [r for r in reservas if r["id"] != reserva_id]
    save_data("reserva.json", reservas)
    return redirect(url_for("listar_reserva"))

@app.route('/solicitacoes/reserva')
def solicitacoes():
    return render_template('solicitacoes.html')

@app.route('/pedido/cliente')
def pedido_cliente():
    return render_template('pedido_cliente.html')

@app.route('/cardapio/cliente', methods=['GET'])
def cardapio_cliente():
   cardapio = load_data('cardapio.json')
   return render_template('cardapio_cliente.html', cardapio=cardapio)

@app.route('/inicio/cliente')
def inicio_cliente():
    return render_template('inicio_cliente.html')

if __name__ == '__main__':
    app.run(debug=True)
