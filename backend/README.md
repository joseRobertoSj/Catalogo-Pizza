# Sistema de Pedidos Inteligente — API Backend

Backend robusto do **Sistema de Pedidos Inteligente**, desenvolvido com **FastAPI**, **SQLAlchemy 2.0** e **Supabase (PostgreSQL)**. Responsável por toda a lógica de negócio, validação de dados e integração com automações externas.

---

## Tecnologias Utilizadas

| Tecnologia | Versão | Função |
|-----------|--------|--------|
| **FastAPI** | ≥ 0.110.0 | Framework web assíncrono de alta performance |
| **Uvicorn** | ≥ 0.28.0 | Servidor ASGI para produção |
| **SQLAlchemy** | ≥ 2.0.28 | ORM para mapeamento objeto-relacional |
| **Pydantic v2** | ≥ 2.6.4 | Validação estrita de schemas e serialização |
| **psycopg2-binary** | ≥ 2.9.9 | Driver nativo PostgreSQL |
| **python-dotenv** | ≥ 1.0.1 | Carregamento seguro de variáveis `.env` |
| **requests** | ≥ 2.31.0 | Chamadas HTTP para webhooks (n8n) |

---

## Estrutura de Diretórios

```text
backend/
├── app/
│   ├── __init__.py        # Inicialização do módulo Python
│   ├── main.py            # App FastAPI, CORS, rotas, seed de dados, webhook
│   ├── database.py        # Engine SQLAlchemy + sessão com Supabase (.env)
│   ├── models.py          # Tabelas ORM: produtos, pedidos, itens_pedido
│   └── schemas.py         # Schemas Pydantic v2 com field_validators
├── .env                   # DATABASE_URL do Supabase (NÃO versionado)
└── requirements.txt       # Dependências Python
```

---

## Banco de Dados (Supabase — PostgreSQL)

### Tabelas

| Tabela | Descrição | Relacionamentos |
|--------|-----------|----------------|
| `produtos` | Catálogo de itens (nome, preço, categoria, imagem, status ativo) | — |
| `pedidos` | Registro de pedidos com dados do cliente e total calculado | 1:N → `itens_pedido` |
| `itens_pedido` | Itens individuais de cada pedido com preço unitário congelado | N:1 → `pedidos`, N:1 → `produtos` |

### Inicialização Automática

- No primeiro boot, `Base.metadata.create_all()` cria todas as tabelas automaticamente.
- Se o banco estiver vazio, a API injeta **6 produtos premium de demonstração** (2 pizzas, 2 doces, 2 bebidas) com fotos profissionais do Unsplash.

---

## Rotas da API

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Status da API + link para documentação |
| `GET` | `/produtos` | Lista produtos ativos. Filtro: `?categoria=pizzas` |
| `GET` | `/produtos/{id}` | Detalhes de um produto específico |
| `POST` | `/pedidos` | Checkout completo com validação centralizada |

### Validações do Checkout (`POST /pedidos`)

1. **Carrinho vazio** → `400 Bad Request`
2. **Telefone inválido** → `422 Unprocessable Entity` (Regex brasileiro)
3. **Nome com menos de 2 caracteres** → `422 Unprocessable Entity`
4. **Produto inexistente ou inativo** → `404 Not Found`
5. **Cálculo seguro** → O preço é sempre buscado do banco, nunca do cliente

---

## Como Iniciar Localmente

### Pré-requisitos
- **Python 3.10+** instalado
- Conta no **Supabase** com um projeto PostgreSQL ativo

### Instalação

```bash
# Navegue até a pasta do backend
cd backend

# Instale as dependências
pip install -r requirements.txt
```

### Configuração do `.env`

Crie um arquivo `.env` na raiz do backend com a URL de conexão do Supabase:

```env
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

### Executar

```bash
python -m uvicorn app.main:app --reload
```

- **API:** http://127.0.0.1:8000
- **Swagger (Documentação Interativa):** http://127.0.0.1:8000/docs

---

## Diretriz Crítica: Validação Centralizada

> Toda validação de regras de negócio é de responsabilidade **exclusiva** da API.
> O frontend não valida formulários — ele apenas renderiza mensagens de erro retornadas pelo backend.

Isso garante:
- **Segurança:** Preços calculados no servidor, não no cliente
- **Consistência:** Uma única fonte de verdade para todas as regras
- **Manutenibilidade:** Alterações de regras em um único lugar

---

## Segurança em Produção

- Restringir `allow_origins` no CORS para o domínio do frontend
- Implementar Rate Limiting com `slowapi` no endpoint `POST /pedidos`
- Migrar `.env` para variáveis de ambiente do servidor de hospedagem
