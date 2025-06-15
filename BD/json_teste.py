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
def index():
    cardapio = load_data("cardapio.json")
    mesas = load_data("mesa.json")
    pedidos = load_data("pedido.json")
    reservas = load_data("reserva.json")

    # Marca as mesas como ocupadas se tiverem uma reserva
    mesas_ocupadas = {int(r["mesa_id"]) for r in reservas}
    for mesa in mesas:
        mesa["ocupada"] = int(mesa["id"]) in mesas_ocupadas

    return render_template("index.html", cardapio=cardapio, mesas=mesas, pedidos=pedidos, reservas=reservas)

# ---------- CRUD CARDÁPIO ----------
@app.route("/adicionar_cardapio", methods=["POST"])
def adicionar_cardapio():
    cardapio = load_data("cardapio.json")
    item = request.form.to_dict()
    item["id"] = len(cardapio) + 1
    cardapio.append(item)
    save_data("cardapio.json", cardapio)
    return redirect(url_for("index"))

@app.route("/editar_cardapio/<int:item_id>", methods=["POST"])
def editar_cardapio(item_id):
    cardapio = load_data("cardapio.json")
    for item in cardapio:
        if item["id"] == item_id:
            item.update(request.form.to_dict())
            break
    save_data("cardapio.json", cardapio)
    return redirect(url_for("index"))

@app.route("/excluir_cardapio/<int:item_id>")
def excluir_cardapio(item_id):
    cardapio = load_data("cardapio.json")
    cardapio = [item for item in cardapio if item["id"] != item_id]
    save_data("cardapio.json", cardapio)
    return redirect(url_for("index"))

# ---------- CRUD MESAS ----------
@app.route("/adicionar_mesa", methods=["POST"])
def adicionar_mesa():
    mesas = load_data("mesa.json")
    nova = request.form.to_dict()
    nova["id"] = len(mesas) + 1
    mesas.append(nova)
    save_data("mesa.json", mesas)
    return redirect(url_for("index"))

@app.route("/editar_mesa/<int:mesa_id>", methods=["POST"])
def editar_mesa(mesa_id):
    mesas = load_data("mesa.json")
    for m in mesas:
        if m["id"] == mesa_id:
            m.update(request.form.to_dict())
            break
    save_data("mesa.json", mesas)
    return redirect(url_for("index"))

@app.route("/excluir_mesa/<int:mesa_id>")
def excluir_mesa(mesa_id):
    mesas = load_data("mesa.json")
    mesas = [m for m in mesas if m["id"] != mesa_id]
    save_data("mesa.json", mesas)
    return redirect(url_for("index"))

# ---------- CRUD PEDIDOS ----------
@app.route("/adicionar_pedido", methods=["POST"])
def adicionar_pedido():
    pedidos = load_data("pedido.json")
    novo = request.form.to_dict()
    novo["id"] = len(pedidos) + 1
    pedidos.append(novo)
    save_data("pedido.json", pedidos)
    return redirect(url_for("index"))

@app.route("/editar_pedido/<int:pedido_id>", methods=["POST"])
def editar_pedido(pedido_id):
    pedidos = load_data("pedido.json")
    for p in pedidos:
        if p["id"] == pedido_id:
            p.update(request.form.to_dict())
            break
    save_data("pedido.json", pedidos)
    return redirect(url_for("index"))

@app.route("/excluir_pedido/<int:pedido_id>")
def excluir_pedido(pedido_id):
    pedidos = load_data("pedido.json")
    pedidos = [p for p in pedidos if p["id"] != pedido_id]
    save_data("pedido.json", pedidos)
    return redirect(url_for("index"))

# ---------- CRUD RESERVAS ----------
@app.route("/adicionar_reserva", methods=["POST"])
def adicionar_reserva():
    reservas = load_data("reserva.json")
    nova = request.form.to_dict()
    nova["id"] = len(reservas) + 1
    reservas.append(nova)
    save_data("reserva.json", reservas)
    return redirect(url_for("index"))

@app.route("/excluir_reserva/<int:reserva_id>")
def excluir_reserva(reserva_id):
    reservas = load_data("reserva.json")
    reservas = [r for r in reservas if r["id"] != reserva_id]
    save_data("reserva.json", reservas)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
