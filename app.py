from flask import Flask, request, render_template, redirect, url_for, jsonify, session, flash
import json
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '123456')

DADOS_DIR = 'dados'

def ler_json(nome_arquivo):
    try:
        caminho = os.path.join(DADOS_DIR, nome_arquivo)
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"Arquivo {nome_arquivo} não encontrado")
        with open(caminho, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise ValueError(f"Arquivo {nome_arquivo} contém JSON inválido")
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo {nome_arquivo}: {str(e)}")

def salvar_json(nome_arquivo, dados):
    try:
        with open(os.path.join(DADOS_DIR, nome_arquivo), 'w') as f:
            json.dump(dados, f, indent=4)
    except Exception as e:
        flash(f'Erro ao salvar dados: {str(e)}')
        raise

def buscar_item_por_id(items, id):
    return next((item for item in items if item['id'] == id), None)

def atualizar_item(items, id, novos_dados):
    for i, item in enumerate(items):
        if item['id'] == id:
            items[i].update(novos_dados)
            return True
    return False

def validar_dados_cardapio(dados):
    erros = []
    if not dados.get('nome'):
        erros.append('Nome é obrigatório')
    if not dados.get('preco') or not str(dados['preco']).replace('.', '').isdigit():
        erros.append('Preço inválido')
    return erros

def validar_pedido(dados):
    erros = []
    campos_obrigatorios = ['id_mesa', 'id_cardapio', 'quantidade']
    for campo in campos_obrigatorios:
        if campo not in dados:
            erros.append(f"Campo {campo} é obrigatório")
    if 'quantidade' in dados and not str(dados['quantidade']).isdigit():
        erros.append("Quantidade deve ser um número")
    return erros

def gerar_id(items):
    if not items:
        return 1
    # Verifica se é uma lista de pedidos (usa id_pedido) ou outros itens (usa id)
    id_key = 'id_pedido' if 'id_pedido' in items[0] else 'id'
    return max(item[id_key] for item in items) + 1

def adicionar_pedido():
    """
    Adiciona um novo pedido ao sistema.
    
    Returns:
        redirect: Redireciona para a página de pedidos em caso de sucesso
        ou para a página de erro em caso de falha.
    """
    pass

#proteção de rotas e gerenciamento de sessão
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

#Rotas de autenticação
@app.route('/login')
def login():
    return render_template('login.html')
        
@app.route('/login/cliente', methods=['GET', 'POST'])
def login_cliente():
    if request.method == 'POST':
        try:
            # Verifica se os campos foram preenchidos
            if not request.form.get('email') or not request.form.get('senha'):
                flash('Por favor, preencha todos os campos', 'error')
                return redirect(url_for('login_cliente'))

            # Carrega os clientes
            clientes = ler_json('cliente.json')
            
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
            admins = ler_json('admin.json')
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
        # Verifica se todos os campos obrigatórios foram preenchidos
        if not all(k in request.form for k in ['nome', 'email', 'senha', 'confirmar_senha']):
            flash('Todos os campos são obrigatórios', 'error')
            return redirect(url_for('cadastro_cliente'))
        
        # Verifica se as senhas coincidem
        if request.form['senha'] != request.form['confirmar_senha']:
            flash('As senhas não coincidem. Por favor, tente novamente.', 'error')
            return redirect(url_for('cadastro_cliente'))
        
        try:
            clientes = ler_json('cliente.json')
            # Verifica se o email já está cadastrado
            if any(c['email'] == request.form['email'] for c in clientes):
                flash('Este email já está cadastrado. Por favor, use outro email.', 'error')
                return redirect(url_for('cadastro_cliente'))
            
            novo_cliente = {
                "id": gerar_id(clientes),
                "nome": request.form['nome'],
                "email": request.form['email'],
                "senha": generate_password_hash(request.form['senha'])
            }
            clientes.append(novo_cliente)
            salvar_json('cliente.json', clientes)
            
            # Fazer login automático após o cadastro
            session['usuario_id'] = novo_cliente['id']
            session['tipo_usuario'] = 'cliente'
            
            flash('Cadastro realizado com sucesso! Bem-vindo ao sistema.', 'success')
            return redirect(url_for('inicio_cliente'))
        except Exception as e:
            flash(f'Erro ao realizar cadastro: {str(e)}', 'error')
            return redirect(url_for('cadastro_cliente'))
    return render_template('cadastro_cliente.html')


@app.route('/')
def index():
    return render_template('tela_inicial.html')

#Rotas do cliente
@app.route('/cliente/cardapio')
@login_required
def cardapio_cliente():
    try:
        pratos = ler_json('cardapio.json')
        mesas = ler_json('mesa.json')
        mesas_disponiveis = [m for m in mesas if m['status'] == 'livre']
        
        # Carrega os dados do cliente
        clientes = ler_json('cliente.json')
        cliente = next((c for c in clientes if c['id'] == session.get('user_id')), None)
        
        return render_template('cardapio_cliente.html', pratos=pratos, mesas=mesas_disponiveis, cliente=cliente)
    except Exception as e:
        flash(f'Erro ao carregar cardápio: {str(e)}', 'error')
        return redirect(url_for('inicio_cliente'))

@app.route('/cliente/pedidos')
@login_required
def pedidos_cliente():
    try:
        pedidos = ler_json('pedido.json')
        cardapio = ler_json('cardapio.json')
        
        # Filtra os pedidos do cliente atual
        pedidos_cliente = [p for p in pedidos if p.get('id_cliente') == session.get('user_id')]
        
        # Adiciona o nome do prato a cada pedido
        for pedido in pedidos_cliente:
            # Converte os IDs para inteiros para comparação
            id_cardapio = int(pedido['id_cardapio'])
            prato = next((p for p in cardapio if int(p['id']) == id_cardapio), None)
            if prato:
                pedido['nome_prato'] = prato['nome']
            else:
                pedido['nome_prato'] = 'Prato não encontrado'
        
        # Carrega os dados do cliente
        clientes = ler_json('cliente.json')
        cliente = next((c for c in clientes if c['id'] == session.get('user_id')), None)
        
        return render_template('pedido_cliente.html', pedidos=pedidos_cliente, cliente=cliente)
    except Exception as e:
        flash(f'Erro ao carregar pedidos: {str(e)}', 'error')
        return redirect(url_for('inicio_cliente'))

@app.route('/cliente/pedido/adicionar', methods=['POST'])
@login_required
def cliente_adicionar_pedido():
    if request.method == 'POST':
        try:
            # Validar os dados do formulário
            erros = validar_pedido(request.form)
            if erros:
                for erro in erros:
                    flash(erro, 'error')
                return redirect(url_for('cardapio_cliente'))

            # Ler os pedidos existentes
            pedidos = ler_json('pedido.json')
            
            # Criar novo pedido
            novo_pedido = {
                "id_pedido": gerar_id(pedidos),
                "id_mesa": request.form['id_mesa'],
                "id_cardapio": request.form['id_cardapio'],
                "id_cliente": session.get('user_id'),  # Adiciona o ID do cliente
                "quantidade": int(request.form['quantidade']),
                "status": "pendente",  # Status inicial sempre pendente
                "observacoes": request.form.get('observacoes', '')
            }
            
            # Adicionar o novo pedido à lista
            pedidos.append(novo_pedido)
            
            # Salvar a lista atualizada
            salvar_json('pedido.json', pedidos)
            
            flash('Pedido adicionado com sucesso', 'success')
            return redirect(url_for('pedidos_cliente'))
        except Exception as e:
            flash(f'Erro ao adicionar pedido: {str(e)}', 'error')
            return redirect(url_for('cardapio_cliente'))

#Rotas do admin
@app.route('/admin', methods=['GET'])
@login_required
@admin_required
def admin():
    try:
        return render_template('admin.html')
    except Exception as e:
        flash(f'Erro ao carregar página: {str(e)}')
        return redirect(url_for('login'))

@app.route('/admin/mesas', methods=['GET'])
@login_required
@admin_required
def mesas():
    try:
        mesas = ler_json('mesa.json')
        return render_template('mesas.html', mesas=mesas)
    except FileNotFoundError:
        flash('Erro ao carregar mesas')
        return redirect(url_for('admin'))
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}')
        return redirect(url_for('admin'))

@app.route('/admin/cardapio', methods=['GET'])
@admin_required
def cardapio():
    try:
        pratos = ler_json('cardapio.json')
        return render_template('cardapio.html', pratos=pratos)
    except Exception as e:
        flash(f'Erro ao carregar cardápio: {str(e)}')
        return redirect(url_for('admin'))

@app.route('/admin/pedidos', methods=['GET'])
@admin_required
def pedidos():
    try:
        pedidos = ler_json('pedido.json')
        return render_template('pedidos.html', pedidos=pedidos)
    except FileNotFoundError:
        # Se o arquivo não existir, cria um array vazio
        with open(os.path.join(DADOS_DIR, 'pedido.json'), 'w') as f:
            json.dump([], f)
        return render_template('pedidos.html', pedidos=[])
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}')
        return redirect(url_for('admin'))

@app.route('/admin/reserva', methods=['GET'])
@admin_required
def admin_reserva():
    try:
        reservas = ler_json('reserva.json')
        return render_template('reserva.html', reservas=reservas)
    except FileNotFoundError:
        flash('Erro ao carregar reservas')
        return redirect(url_for('admin'))
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}')
        return redirect(url_for('admin'))

@app.route('/admin/reserva/adicionar', methods=['GET', 'POST'])
@admin_required
def adicionar_reserva():
    if request.method == 'POST':
        erros = validar_reserva(request.form)
        if erros:
            for erro in erros:
                flash(erro)
            return redirect(url_for('adicionar_reserva'))
        
        try:
            reserva = ler_json('reserva.json')
            nova_reserva = {
                "id_reserva": request.form['id_reserva'],
                "data_confirmacao": request.form['data_confirmacao']
            }
            if not validar_data(request.form['data_confirmacao']):
                flash('Data inválida. Use o formato YYYY-MM-DD')
                return redirect(url_for('adicionar_reserva'))
            
            reserva.append(nova_reserva)
            salvar_json('reserva.json', reserva)
            flash('Reserva adicionada com sucesso')
            return redirect(url_for('admin_reserva'))
        except Exception as e:
            flash(f'Erro ao adicionar reserva: {str(e)}')
            return redirect(url_for('adicionar_reserva'))
    return render_template('adicionar_reserva.html')

@app.route('/admin/adicionar/pedido', methods=['GET', 'POST'])
@admin_required
def adicionar_pedido_admin():
    if request.method == 'POST':
        try:
            # Validar os dados do formulário
            erros = validar_pedido(request.form)
            if erros:
                for erro in erros:
                    flash(erro)
                return redirect(url_for('adicionar_pedido_admin'))

            # Ler os pedidos existentes
            pedidos = ler_json('pedido.json')
            
            # Criar novo pedido
            novo_pedido = {
                "id_pedido": gerar_id(pedidos),
                "id_mesa": request.form['id_mesa'],
                "id_cardapio": request.form['id_cardapio'],
                "quantidade": int(request.form['quantidade']),
                "status": request.form['status'],
                "observacoes": request.form['observacoes']
            }
            
            # Adicionar o novo pedido à lista
            pedidos.append(novo_pedido)
            
            # Salvar a lista atualizada
            salvar_json('pedido.json', pedidos)
            
            flash('Pedido adicionado com sucesso')
            return redirect(url_for('pedidos'))
        except Exception as e:
            flash(f'Erro ao adicionar pedido: {str(e)}')
            return redirect(url_for('adicionar_pedido_admin'))
    
    try:
        mesas = ler_json('mesa.json')
        pratos = ler_json('cardapio.json')
        return render_template('adicionar_pedido.html', mesas=mesas, pratos=pratos)
    except Exception as e:
        flash(f'Erro ao carregar dados: {str(e)}')
        return redirect(url_for('pedidos'))

@app.route('/admin/cardapio/adicionar', methods=['GET', 'POST'])
@admin_required
def adicionar_cardapio():
    if request.method == 'POST':
        erros = validar_cardapio(request.form)
        if erros:
            for erro in erros:
                flash(erro)
            return redirect(url_for('adicionar_cardapio'))
        
        try:
            cardapio = ler_json('cardapio.json')
            novo_cardapio = {
                "id": gerar_id(cardapio),
                "nome": request.form['nome'],
                "descricao": request.form['descricao'],     
                "ingredientes": request.form['ingredientes'],
                "preco": float(request.form['preco']),
                "categoria": request.form['categoria']
            }
            cardapio.append(novo_cardapio)
            salvar_json('cardapio.json', cardapio)
            flash('Item adicionado ao cardápio com sucesso')
            return redirect(url_for('cardapio'))
        except Exception as e:
            flash(f'Erro ao adicionar item: {str(e)}')
            return redirect(url_for('adicionar_cardapio'))
    return render_template('adicionar_cardapio.html')

#Rotas de edição
@app.route('/admin/cardapio/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_cardapio(id):
    try:
        items = ler_json('cardapio.json')
        item = buscar_item_por_id(items, id)
        if not item:
            flash('Item não encontrado')
            return redirect(url_for('cardapio'))
        
        if request.method == 'POST':
            erros = validar_cardapio(request.form)
            if erros:
                for erro in erros:
                    flash(erro)
                return redirect(url_for('editar_cardapio', id=id))
            
            item['nome'] = request.form['nome']
            item['descricao'] = request.form['descricao']
            item['ingredientes'] = request.form['ingredientes']
            item['preco'] = float(request.form['preco'])
            item['categoria'] = request.form['categoria']
            
            # Atualizar na lista original
            for i, it in enumerate(items):
                if it['id'] == id:
                    items[i] = item
                    break
                    
            salvar_json('cardapio.json', items)
            flash('Item atualizado com sucesso')
            return redirect(url_for('cardapio'))
        return render_template('editar_cardapio.html', item=item)
    except Exception as e:
        flash(f'Erro ao editar item: {str(e)}')
        return redirect(url_for('cardapio'))

@app.route('/admin/pedido/editar/<int:id_pedido>', methods=['GET', 'POST'])
@admin_required
def admin_editar_pedido(id_pedido):
    pedidos = ler_json('pedido.json')
    pedido = next((p for p in pedidos if p['id_pedido'] == id_pedido), None)
    if pedido is None:
        flash('Pedido não encontrado')
        return redirect(url_for('pedidos'))

    if request.method == 'POST':
        pedido['quantidade'] = int(request.form['quantidade'])
        pedido['status'] = request.form['status']
        pedido['observacoes'] = request.form['observacoes']
        
        for i, p in enumerate(pedidos):
            if p['id_pedido'] == id_pedido:
                pedidos[i] = pedido
                break
                
        salvar_json('pedido.json', pedidos)
        return redirect(url_for('pedidos'))
    return render_template('editar_pedido.html', pedido=pedido)

@app.route('/cliente/pedido/editar/<int:id_pedido>', methods=['GET', 'POST'])
@login_required
def cliente_editar_pedido(id_pedido):
    pedidos = ler_json('pedido.json')
    pedido = next((p for p in pedidos if p['id_pedido'] == id_pedido), None)
    if pedido is None:
        flash('Pedido não encontrado')
        return redirect(url_for('pedidos_cliente'))

    if request.method == 'POST':
        pedido['quantidade'] = int(request.form['quantidade'])
        pedido['status'] = request.form['status']
        pedido['observacoes'] = request.form['observacoes']
        
        for i, p in enumerate(pedidos):
            if p['id_pedido'] == id_pedido:
                pedidos[i] = pedido
                break
                
        salvar_json('pedido.json', pedidos)
        return redirect(url_for('pedidos_cliente'))
    return render_template('editar_pedido.html', pedido=pedido)
    
@app.route('/admin/reserva/editar/<int:id_reserva>', methods=['GET', 'POST'])
@admin_required
def editar_reserva(id_reserva):
    try:
        reservas = ler_json('reserva.json')
        reserva = next((r for r in reservas if str(r['id_reserva']) == str(id_reserva)), None)
        if reserva is None:
            flash('Reserva não encontrada')
            return redirect(url_for('admin_reserva'))
        
        if request.method == 'POST':
            if not validar_data(request.form['data_confirmacao']):
                flash('Data inválida. Use o formato YYYY-MM-DD')
                return redirect(url_for('editar_reserva', id_reserva=id_reserva))
            
            reserva['data_confirmacao'] = request.form['data_confirmacao']
            salvar_json('reserva.json', reservas)
            flash('Reserva atualizada com sucesso')
            return redirect(url_for('admin_reserva'))
        return render_template('editar_reserva.html', reserva=reserva)
    except Exception as e:
        flash(f'Erro ao editar reserva: {str(e)}')
        return redirect(url_for('admin_reserva'))

#Rotas de exclusão
@app.route('/admin/cardapio/excluir/<int:id>', methods=['POST'])
@admin_required
def excluir_cardapio(id):
    items = ler_json('cardapio.json')
    items = [i for i in items if i['id'] != id]
    salvar_json('cardapio.json', items)
    flash('Item excluído com sucesso')
    return redirect(url_for('cardapio'))

@app.route('/admin/pedido/excluir/<int:id_pedido>', methods=['POST'])
@admin_required
def excluir_pedido(id_pedido):
    pedido = ler_json('pedido.json')
    pedido = [p for p in pedido if p['id_pedido'] != id_pedido]
    salvar_json('pedido.json', pedido)
    flash('Pedido excluído com sucesso')
    return redirect(url_for('pedidos'))


@app.route('/cliente/pedido/excluir/<int:id_pedido>', methods=['POST'])
@login_required
def cliente_excluir_pedido(id_pedido):
    pedido = ler_json('pedido.json')
    pedido = [p for p in pedido if p['id_pedido'] != id_pedido]
    salvar_json('pedido.json', pedido)
    flash('Pedido excluído com sucesso')
    return redirect(url_for('pedidos_cliente'))

@app.route('/admin/reserva/excluir/<int:id_reserva>', methods=['POST'])
@admin_required
def excluir_reserva(id_reserva):
    try:
        reservas = ler_json('reserva.json')
        reservas = [r for r in reservas if str(r['id_reserva']) != str(id_reserva)]
        salvar_json('reserva.json', reservas)
        flash('Reserva excluída com sucesso')
    except Exception as e:
        flash(f'Erro ao excluir reserva: {str(e)}')
    return redirect(url_for('admin_reserva'))

# Rotas para visualização
@app.route('/cliente/inicio')
@login_required
def inicio_cliente():
    try:
        # Carrega os dados do cliente
        clientes = ler_json('cliente.json')
        cliente = next((c for c in clientes if c['id'] == session['usuario_id']), None)
        
        if not cliente:
            flash('Erro ao carregar dados do cliente', 'error')
            return redirect(url_for('login_cliente'))
            
        # Carrega as mesas disponíveis
        mesas = ler_json('mesa.json')
        mesas_disponiveis = [m for m in mesas if m['status'] == 'livre']
        
        return render_template('inicio_cliente.html', cliente=cliente, mesas=mesas_disponiveis)
    except Exception as e:
        flash(f'Erro ao carregar página inicial: {str(e)}', 'error')
        return redirect(url_for('login_cliente'))

@app.route('/cliente')
@login_required
def cliente():
    return render_template('inicio_cliente.html')

#Rotas de solicitações
@app.route('/solicitacoes')
def solicitacoes():
    solicitacoes = ler_json('solicitacoes.json')
    return render_template('solicitacoes.html', solicitacoes=solicitacoes)

@app.route('/reserva')
@login_required
def cliente_reserva():
    return render_template('reserva.html')

@app.route('/cliente/reserva/adicionar', methods=['POST'])
@login_required
def cliente_adicionar_reserva():
    if request.method == 'POST':
        erros = validar_reserva(request.form)
        if erros:
            for erro in erros:
                flash(erro)
            return redirect(url_for('cliente'))
        
        try:
            reserva = ler_json('reserva.json')
            nova_reserva = {
                "id_reserva": request.form['id_reserva'],
                "data_confirmacao": request.form['data_confirmacao'],
                "id_cliente": session['usuario_id']
            }
            if not validar_data(request.form['data_confirmacao']):
                flash('Data inválida. Use o formato YYYY-MM-DD')
                return redirect(url_for('cliente'))
            
            reserva.append(nova_reserva)
            salvar_json('reserva.json', reserva)
            flash('Reserva solicitada com sucesso')
            return redirect(url_for('cliente'))
        except Exception as e:
            flash(f'Erro ao solicitar reserva: {str(e)}')
            return redirect(url_for('cliente'))

#Rotas de erro tratamento de erros global
@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def erro_interno(e):
    return render_template('500.html'), 500

def validar_mesa(dados):
    erros = []
    if 'numero' not in dados:
        erros.append('Número da mesa é obrigatório')
    elif not str(dados['numero']).isdigit():
        erros.append('Número da mesa deve ser um número')
    if 'status' not in dados:
        erros.append('Status é obrigatório')
    return erros

def validar_reserva(dados):
    erros = []
    campos_obrigatorios = ['id_reserva', 'data_confirmacao']
    for campo in campos_obrigatorios:
        if campo not in dados or not dados[campo].strip():
            erros.append(f'Campo {campo} é obrigatório')
    return erros

def validar_cardapio(dados):
    erros = []
    campos_obrigatorios = ['nome', 'descricao', 'ingredientes', 'preco', 'categoria']
    for campo in campos_obrigatorios:
        if campo not in dados or not dados[campo].strip():
            erros.append(f'Campo {campo} é obrigatório')
    
    if 'preco' in dados:
        try:
            float(dados['preco'])
        except ValueError:
            erros.append('Preço deve ser um número válido')
    
    return erros

def validar_status(status):
    status_validos = ['pendente', 'em_preparo', 'pronto', 'entregue']
    return status in status_validos

def validar_data(data_str):
    try:
        datetime.strptime(data_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/mesa/excluir/<int:id>', methods=['POST'])
@login_required
@admin_required
def excluir_mesa(id):
    try:
        mesas = ler_json('mesa.json')
        mesas = [m for m in mesas if m['id'] != id]
        salvar_json('mesa.json', mesas)
        flash('Mesa excluída com sucesso')
    except Exception as e:
        flash(f'Erro ao excluir mesa: {str(e)}')
    return redirect(url_for('mesas'))

@app.route('/admin/mesa/adicionar', methods=['GET', 'POST'])
@login_required
@admin_required
def adicionar_mesa():
    if request.method == 'POST':
        erros = validar_mesa(request.form)
        if erros:
            for erro in erros:
                flash(erro)
            return redirect(url_for('adicionar_mesa'))
        try:
            mesas = ler_json('mesa.json')
            nova_mesa = {
                "id": gerar_id(mesas),
                "numero": request.form['numero'],
                "status": request.form['status']
            }
            mesas.append(nova_mesa)
            salvar_json('mesa.json', mesas)
            flash('Mesa adicionada com sucesso')
            return redirect(url_for('mesas'))
        except Exception as e:
            flash(f'Erro ao adicionar mesa: {str(e)}')
            return redirect(url_for('adicionar_mesa'))
    return render_template('adicionar_mesa.html')

if __name__ == '__main__':
    # Criar o arquivo se não existir
    if not os.path.exists(os.path.join(DADOS_DIR, 'pedido.json')):
        with open(os.path.join(DADOS_DIR, 'pedido.json'), 'w') as f:
            json.dump([], f)
>>>>>>> Stashed changes
    app.run(debug=True)
