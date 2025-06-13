from flask import Flask, request, render_template, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)
DADOS_DIR = 'dados'

def ler_json(nome_arquivo):
    caminho = os.path.join(DADOS_DIR, nome_arquivo)
    if not os.path.exists(caminho):
        with open(caminho, 'w') as f:
            json.dump([], f)
    with open(caminho, 'r') as f:
        return json.load(f)

def salvar_json(nome_arquivo, dados):
    with open(os.path.join(DADOS_DIR, nome_arquivo), 'w') as f:
        json.dump(dados, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cardapio')
def cardapio():
    pratos = ler_json('cardapio.json')
    return render_template('cardapio.html', pratos=pratos)

@app.route('/cardapio/adicionar', methods=['POST'])
def adicionar_prato():
    pratos = ler_json('cardapio.json')
    novo_prato = {
        "id": len(pratos) + 1,
        "nome": request.form['nome'],
        "descricao": request.form['descricao'],
        "preco": float(request.form['preco']),
        "categoria": request.form['categoria']
    }
    pratos.append(novo_prato)
    salvar_json('cardapio.json', pratos)
    return redirect(url_for('cardapio'))

@app.route('/mesas')
def mesas():
    mesas = ler_json('mesa.json')
    return render_template('mesas.html', mesas=mesas)

@app.route('/mesas/adicionar', methods=['POST'])
def adicionar_mesa():
    mesas = ler_json('mesa.json')
    nova_mesa = {
        "id": len(mesas) + 1,
        "numero": request.form['numero'],
        "status": "disponível"
    }
    mesas.append(nova_mesa)
    salvar_json('mesa.json', mesas)
    return redirect(url_for('mesas'))

@app.route('/pedidos')
def pedidos():
    pedidos = ler_json('pedido.json')
    return render_template('pedidos.html', pedidos=pedidos)

@app.route('/pedidos/adicionar', methods=['POST'])
def adicionar_pedido():
    pedidos = ler_json('pedido.json')
    novo_pedido = {
        "id": len(pedidos) + 1,
        "mesa_id": int(request.form['mesa_id']),
        "prato": request.form['prato'],
        "status": "em preparo",
        "observacoes": request.form['observacoes']
    }
    pedidos.append(novo_pedido)
    salvar_json('pedido.json', pedidos)
    return redirect(url_for('pedidos'))

if __name__ == '__main__':
    app.run(debug=True)
