from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import requests

from .database import engine, Base, get_db
from . import models, schemas

# Inicializar as tabelas no Supabase caso elas ainda não existam
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Pedidos Inteligente API",
    description="Backend robusto para o delivery integrado com Supabase e WhatsApp",
    version="1.0.0"
)

# Configuração de CORS - Permite que o frontend Vue.js consuma a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique a URL do seu frontend Vercel/Netlify
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- POPULAR BANCO DE DADOS (SEED) ---
# Se o banco de dados Supabase estiver totalmente vazio, insere alguns itens padrão para a demonstração
def popular_banco_se_vazio(db: Session):
    if db.query(models.Produto).count() == 0:
        produtos_seed = [
            models.Produto(
                nome="Pizza Calabresa Gourmet",
                descricao="Molho artesanal, mussarela premium, calabresa defumada especial, cebola roxa e orégano fresco.",
                preco=Decimal("45.00"),
                categoria="pizzas",
                url_imagem="https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=300",
                ativo=True
            ),
            models.Produto(
                nome="Pizza Margherita Clássica",
                descricao="Molho de tomate italiano, mussarela especial, fatias de tomate fresco, manjericão gigante e azeite extra virgem.",
                preco=Decimal("42.00"),
                categoria="pizzas",
                url_imagem="https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?q=80&w=300",
                ativo=True
            ),
            models.Produto(
                nome="Caixa de Brigadeiro Gourmet",
                descricao="Caixa premium com 6 brigadeiros feitos com chocolate belga e confeitos selecionados.",
                preco=Decimal("24.00"),
                categoria="doces",
                url_imagem="https://images.unsplash.com/photo-1548907040-4d42b52115ca?q=80&w=300",
                ativo=True
            ),
            models.Produto(
                nome="Brownie com Nutella",
                descricao="Brownie molhadinho por dentro, com casquinha crocante e cobertura generosa de Nutella pura.",
                preco=Decimal("12.50"),
                categoria="doces",
                url_imagem="https://images.unsplash.com/photo-1606313564200-e75d5e30476c?q=80&w=300",
                ativo=True
            ),
            models.Produto(
                nome="Coca-Cola 2L Gelada",
                descricao="Refrigerante Coca-Cola garrafa de 2 litros bem gelada para acompanhar seu pedido.",
                preco=Decimal("11.00"),
                categoria="bebidas",
                url_imagem="https://images.unsplash.com/photo-1622483767028-3f66f32aef97?q=80&w=300",
                ativo=True
            ),
            models.Produto(
                nome="Suco Natural de Laranja 500ml",
                descricao="Suco 100% natural, espremido na hora. Sem açúcar e sem conservantes.",
                preco=Decimal("8.00"),
                categoria="bebidas",
                url_imagem="https://images.unsplash.com/photo-1613478223719-2ab802602423?q=80&w=300",
                ativo=True
            ),
        ]
        db.add_all(produtos_seed)
        db.commit()

# --- ROTA DE SEED MANUAL / CHECAGEM ---
@app.on_event("startup")
def startup_db_check():
    db = next(get_db())
    try:
        popular_banco_se_vazio(db)
    finally:
        db.close()


# --- ROTAS DA API ---

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "mensagem": "API do Sistema de Pedidos Inteligente ativa!",
        "documentacao": "/docs"
    }

# 1. Obter lista de produtos ativos
@app.get("/produtos", response_model=List[schemas.ProdutoResponse])
def listar_produtos(categoria: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Produto).filter(models.Produto.ativo == True)
    if categoria:
        query = query.filter(models.Produto.categoria == categoria)
    return query.all()

# 2. Obter detalhes de um produto
@app.get("/produtos/{produto_id}", response_model=schemas.ProdutoResponse)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id, models.Produto.ativo == True).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado ou inativo no catálogo."
        )
    return produto

# --- ROTAS ADMINISTRATIVAS (CRUD) ---

# Função auxiliar para verificar autenticação simples do admin
def verificar_admin_token(x_admin_token: Optional[str] = Header(None)):
    if x_admin_token != "sabor-arte-admin-secreto":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso não autorizado! Chave de administração inválida."
        )

# A. Listar todos os produtos (incluindo ativos e inativos) no Painel Admin
@app.get("/admin/produtos", response_model=List[schemas.ProdutoResponse])
def admin_listar_produtos(db: Session = Depends(get_db), token: None = Depends(verificar_admin_token)):
    return db.query(models.Produto).order_by(models.Produto.id.desc()).all()

# B. Criar novo produto
@app.post("/produtos", response_model=schemas.ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(produto_data: schemas.ProdutoCreate, db: Session = Depends(get_db), token: None = Depends(verificar_admin_token)):
    # Evitar duplicados pelo nome
    existente = db.query(models.Produto).filter(models.Produto.nome == produto_data.nome).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um produto cadastrado com o nome '{produto_data.nome}'."
        )
    
    novo_produto = models.Produto(
        nome=produto_data.nome,
        descricao=produto_data.descricao,
        preco=Decimal(str(produto_data.preco)),
        categoria=produto_data.categoria,
        url_imagem=produto_data.url_imagem,
        ativo=produto_data.ativo if produto_data.ativo is not None else True
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto

# C. Atualizar produto existente
@app.put("/produtos/{produto_id}", response_model=schemas.ProdutoResponse)
def atualizar_produto(produto_id: int, produto_data: schemas.ProdutoUpdate, db: Session = Depends(get_db), token: None = Depends(verificar_admin_token)):
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    
    # Atualizar campos enviados
    if produto_data.nome is not None:
        produto.nome = produto_data.nome
    if produto_data.descricao is not None:
        produto.descricao = produto_data.descricao
    if produto_data.preco is not None:
        produto.preco = Decimal(str(produto_data.preco))
    if produto_data.categoria is not None:
        produto.categoria = produto_data.categoria
    if produto_data.url_imagem is not None:
        produto.url_imagem = produto_data.url_imagem
    if produto_data.ativo is not None:
        produto.ativo = produto_data.ativo

    db.commit()
    db.refresh(produto)
    return produto

# D. Excluir produto (Exclusão Inteligente)
@app.delete("/produtos/{produto_id}")
def excluir_produto(produto_id: int, db: Session = Depends(get_db), token: None = Depends(verificar_admin_token)):
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    
    # Verificar se o produto já está em algum pedido
    em_uso = db.query(models.ItemPedido).filter(models.ItemPedido.produto_id == produto_id).first()
    if em_uso:
        # Se já foi ordenado, apenas desativa para preservar histórico de vendas
        produto.ativo = False
        db.commit()
        return {
            "status": "Sucesso",
            "mensagem": f"O produto '{produto.nome}' está em uso em pedidos passados. Ele foi desativado do catálogo para preservar o histórico."
        }
    
    # Se nunca foi ordenado, deleta fisicamente
    db.delete(produto)
    db.commit()
    return {
        "status": "Sucesso",
        "mensagem": f"O produto '{produto.nome}' foi removido permanentemente do banco de dados."
    }

# Função auxiliar para disparar o webhook do n8n em segundo plano (Background Task)
def disparar_webhook_n8n(url: str, payload: dict, user: Optional[str] = None, password: Optional[str] = None):
    try:
        auth = (user, password) if user and password else None
        response = requests.post(url, json=payload, auth=auth, timeout=10.0)
        print(f"[n8n Webhook] Disparado com sucesso via tarefa em segundo plano! Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[n8n Webhook Error] Falha ao enviar requisição para o n8n: {e}")

# 3. Criar novo pedido (Checkout)
@app.post("/pedidos", status_code=status.HTTP_201_CREATED)
def criar_pedido(pedido_data: schemas.PedidoCreateSchema, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Validação do Carrinho (Diretriz Crítica de Centralização no Backend)
    if not pedido_data.itens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seu carrinho está vazio. Adicione pelo menos um item para fechar o pedido."
        )

    total_acumulado = Decimal("0.00")
    itens_para_salvar = []

    # Validar produtos e calcular totais com segurança usando preços da API (nunca confiar no preço do cliente)
    for item in pedido_data.itens:
        produto = db.query(models.Produto).filter(models.Produto.id == item.produto_id, models.Produto.ativo == True).first()
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"O produto de ID {item.produto_id} não existe ou foi removido do catálogo."
            )
        
        # Calcular preço do subtotal do item
        subtotal_item = produto.preco * item.quantidade
        total_acumulado += subtotal_item

        # Criar instância do Item do Pedido
        item_pedido = models.ItemPedido(
            produto_id=produto.id,
            quantidade=item.quantidade,
            preco_unitario=produto.preco
        )
        itens_para_salvar.append((item_pedido, produto.nome))

    # Criar registro do Pedido
    novo_pedido = models.Pedido(
        nome_cliente=pedido_data.nome_cliente,
        telefone=pedido_data.telefone,
        endereco_entrega=pedido_data.endereco_entrega,
        forma_pagamento=pedido_data.forma_pagamento,
        total=total_acumulado,
        status="recebido"
    )

    db.add(novo_pedido)
    db.flush()  # Gera o ID do pedido antes do commit definitivo

    # Associar e salvar itens
    for item_inst, nome_prod in itens_para_salvar:
        item_inst.pedido_id = novo_pedido.id
        db.add(item_inst)

    db.commit()
    db.refresh(novo_pedido)

    # --- SIMULAÇÃO OU GATILHO DE WEBHOOK (n8n / Make.com) ---
    # Aqui prepararemos o disparo do webhook futuramente. 
    # Por enquanto, logamos o payload que será enviado à automação.
    payload_webhook = {
        "pedido_id": novo_pedido.id,
        "cliente": novo_pedido.nome_cliente,
        "telefone": novo_pedido.telefone,
        "endereco": novo_pedido.endereco_entrega,
        "forma_pagamento": novo_pedido.forma_pagamento,
        "total": float(novo_pedido.total),
        "status": novo_pedido.status,
        "itens": [
            {
                "produto": nome_p,
                "quantidade": item.quantidade,
                "preco_unitario": float(item.preco_unitario)
            }
            for item, nome_p in itens_para_salvar
        ]
    }

    # --- DISPARO DE WEBHOOK PARA O N8N ---
    import os
    n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
    if n8n_webhook_url:
        try:
            user = os.getenv("N8N_WEBHOOK_USER")
            password = os.getenv("N8N_WEBHOOK_PASSWORD")
            print(f"[n8n Webhook] Agendando disparo em segundo plano para o pedido #{novo_pedido.id}...")
            background_tasks.add_task(
                disparar_webhook_n8n, 
                n8n_webhook_url, 
                payload_webhook, 
                user, 
                password
            )
        except Exception as e:
            print(f"[n8n Webhook Error] Erro ao agendar tarefa de webhook: {e}")
    else:
        print(f"[n8n Webhook] N8N_WEBHOOK_URL não configurada no .env. Ignorando disparo.")


    return {
        "status": "Sucesso",
        "mensagem": "Pedido recebido e enviado para processamento na cozinha!",
        "pedido_id": novo_pedido.id,
        "total": float(novo_pedido.total)
    }
