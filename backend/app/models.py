from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    preco = Column(Numeric(10, 2), nullable=False)
    categoria = Column(String(50), nullable=True)  # Ex: 'pizzas', 'doces', 'bebidas'
    url_imagem = Column(String(255), nullable=True)
    ativo = Column(Boolean, default=True)

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    nome_cliente = Column(String(150), nullable=False)
    telefone = Column(String(20), nullable=False)
    endereco_entrega = Column(Text, nullable=True)  # Opcional se for retirada
    forma_pagamento = Column(String(50), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(30), default="recebido")  # Ex: 'recebido', 'em_preparacao', 'enviado', 'entregue'

    # Relacionamento de um-para-muitos com os itens do pedido
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)

    # Relacionamentos
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")
