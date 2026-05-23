import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from decimal import Decimal

# --- SCHEMAS DE PRODUTO ---
class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    preco: float
    categoria: Optional[str] = None
    url_imagem: Optional[str] = None
    ativo: bool

    class Config:
        from_attributes = True

class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=2, description="O nome deve conter pelo menos 2 caracteres")
    descricao: Optional[str] = None
    preco: float = Field(..., gt=0, description="O preço deve ser maior que 0")
    categoria: str = Field(..., description="Categoria do produto (ex: pizzas, doces, bebidas)")
    url_imagem: Optional[str] = None
    ativo: Optional[bool] = True

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[float] = None
    categoria: Optional[str] = None
    url_imagem: Optional[str] = None
    ativo: Optional[bool] = None

# --- SCHEMAS DE ITENS DO PEDIDO ---
class ItemPedidoSchema(BaseModel):
    produto_id: int
    quantidade: int = Field(..., gt=0, description="A quantidade deve ser maior que 0")

    class Config:
        from_attributes = True

class ItemPedidoResponse(BaseModel):
    id: int
    produto: ProdutoResponse
    quantidade: int
    preco_unitario: float

    class Config:
        from_attributes = True

# --- SCHEMAS DE PEDIDO ---
class PedidoCreateSchema(BaseModel):
    nome_cliente: str = Field(..., min_length=2, description="O nome deve conter pelo menos 2 caracteres")
    telefone: str = Field(..., description="Telefone de contato do cliente")
    endereco_entrega: Optional[str] = None
    forma_pagamento: str = Field(..., description="Forma de pagamento (ex: PIX, Cartão, Dinheiro)")
    itens: List[ItemPedidoSchema] = Field(..., min_length=1, description="O carrinho deve conter pelo menos 1 item")

    # Validação Centralizada do Telefone (Conforme Diretriz Crítica)
    @field_validator('telefone')
    @classmethod
    def validar_telefone_br(cls, v: str) -> str:
        # Remove caracteres não numéricos para validação limpa (opcional, mas o regex abaixo valida com parênteses, espaço e hífen)
        padrao = r'^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$'
        if not re.match(padrao, v):
            # Toda mensagem e aviso centralizados no backend
            raise ValueError('O número de telefone informado é inválido. Use um formato brasileiro válido (ex: 11999999999 ou (11) 99999-9999).')
        return v

class PedidoResponse(BaseModel):
    id: int
    nome_cliente: str
    telefone: str
    endereco_entrega: Optional[str] = None
    forma_pagamento: str
    total: float
    criado_em: str
    status: str
    itens: List[ItemPedidoResponse]

    class Config:
        from_attributes = True
