# 🔥 Sabor & Arte Delivery

**Sistema de Pedidos Inteligente** — Plataforma completa de delivery digital para micro e pequenas empresas, com cardápio interativo, checkout integrado e notificações automáticas via WhatsApp.

<p align="center">
  <img src="https://img.shields.io/badge/Vue.js-3.5-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white" />
  <img src="https://img.shields.io/badge/Vite-5-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" />
  <img src="https://img.shields.io/badge/n8n-Automação-EA4B71?style=for-the-badge&logo=n8n&logoColor=white" />
</p>

---

## 💡 Sobre o Projeto

Micro e pequenas empresas que operam com delivery enfrentam gargalos severos: anotar pedidos pelo WhatsApp consome tempo, gera erros e afeta a experiência do cliente. Plataformas tradicionais cobram taxas abusivas por transação.

**Sabor & Arte Delivery** resolve isso com um ecossistema próprio e independente:

- **Catálogo digital** otimizado para smartphones com design premium dark mode
- **API robusta** com validação centralizada e cálculo seguro de preços
- **Automação inteligente** que envia o resumo do pedido direto no WhatsApp

---

## ✨ Funcionalidades

### Frontend (Cliente)
- 📱 Interface **Mobile-First** com design obsidian escuro e acentos âmbar gourmet
- 🔍 Filtro por categorias (Pizzas, Doces, Bebidas) com segmented control glassmorphism
- 🛒 Sacola flutuante com contagem de itens e valor total em tempo real
- 📝 Checkout em bottom-sheet com formulário de entrega/retirada
- 💳 Seletor de pagamento visual (PIX, Cartão, Dinheiro)
- ✅ Tela de confirmação animada com checkmark e sparkles
- ⚡ Zero dependências extras — apenas Vue 3 puro

### Backend (API)
- 🔐 Validação centralizada — o frontend **nunca** valida regras de negócio
- 💰 Cálculo seguro de preços — valores buscados do banco, não do cliente
- 📞 Validação de telefone brasileiro via Regex
- 🌱 Seed automático com 6 produtos premium no primeiro boot
- 📖 Documentação Swagger interativa em `/docs`
- 🔗 Payload de webhook pronto para disparo ao n8n

### Automação (n8n)
- 📨 Webhook recebe o pedido completo em JSON
- 📋 Formatação automática da mensagem de resumo
- 📲 Disparo direto para WhatsApp do comerciante e do cliente

---

## 🏗️ Arquitetura

```
┌──────────────────┐       HTTP/JSON        ┌──────────────────────┐
│                  │  ◀─── GET /produtos ──▶ │                      │
│   Vue.js 3 SPA   │                         │   FastAPI Backend     │
│   (Vite 5)       │  ──── POST /pedidos ──▶ │   (Python 3.10+)     │
│                  │                         │                      │
└──────────────────┘                         └──────────┬───────────┘
                                                        │
                                            ┌───────────┼───────────┐
                                            ▼           ▼           ▼
                                      ┌──────────┐ ┌─────────┐ ┌─────────┐
                                      │ Validação │ │ Cálculo │ │Supabase │
                                      │ Pydantic │ │ Seguro  │ │PostgreSQL│
                                      └──────────┘ └─────────┘ └────┬────┘
                                                                     │
                                                              ┌──────▼──────┐
                                                              │  Webhook    │
                                                              │  POST JSON  │
                                                              └──────┬──────┘
                                                                     │
                                                              ┌──────▼──────┐
                                                              │ n8n Workflow │
                                                              │  ──▶ WhatsApp│
                                                              └─────────────┘
```

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| **Frontend** | Vue.js 3 (Composition API) | ^3.5.34 |
| **Bundler** | Vite | ^5.4.1 |
| **Backend** | FastAPI | ≥ 0.110.0 |
| **Servidor** | Uvicorn (ASGI) | ≥ 0.28.0 |
| **ORM** | SQLAlchemy | ≥ 2.0.28 |
| **Validação** | Pydantic v2 | ≥ 2.6.4 |
| **Banco de Dados** | PostgreSQL (Supabase) | — |
| **Automação** | n8n (Webhook) | — |
| **Tipografia** | Outfit (Google Fonts) | — |
| **Iconografia** | Lucide Icons (SVG inline) | — |

---

## 📁 Estrutura do Projeto

```
Portifolio FOREVER/
│
├── 📄 README.md                    ← Você está aqui
├── 📄 .gitignore
├── 📄 Documentação_ Sistema de Pedidos Inteligente.md
│
├── 🔧 backend/
│   ├── README.md
│   ├── requirements.txt
│   ├── .env                        (não versionado)
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app + rotas + seed
│       ├── database.py             # Engine SQLAlchemy + Supabase
│       ├── models.py               # Tabelas ORM
│       └── schemas.py              # Schemas Pydantic v2
│
└── 🎨 frontend/
    ├── README.md
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.js
        ├── style.css               # Design System (920+ linhas CSS puro)
        ├── App.vue                 # Layout raiz + estado do carrinho
        └── components/
            ├── Catalogo.vue        # Cards + filtros + fetch assíncrono
            ├── CarrinhoFlutuante.vue # Barra flutuante da sacola
            └── CheckoutModal.vue   # Modal de checkout completo
```

---

## 🚀 Como Rodar Localmente

### Pré-requisitos

- [Python 3.10+](https://python.org)
- [Node.js 20+](https://nodejs.org)
- Conta no [Supabase](https://supabase.com) com projeto PostgreSQL ativo

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/sabor-arte-delivery.git
cd sabor-arte-delivery
```

### 2. Configure e inicie o Backend

```bash
cd backend
pip install -r requirements.txt

# Crie o arquivo .env com sua URL do Supabase
echo "DATABASE_URL=postgresql://..." > .env

# Inicie a API
python -m uvicorn app.main:app --reload
```

> API rodando em **http://127.0.0.1:8000** — Swagger em **http://127.0.0.1:8000/docs**

### 3. Configure e inicie o Frontend

```bash
cd frontend
npm install
npm run dev
```

> App rodando em **http://localhost:5173**

---

## 🎨 Design System

A interface utiliza um **design system artesanal** construído inteiramente em CSS puro (920+ linhas), sem frameworks de UI:

| Aspecto | Implementação |
|---------|--------------|
| **Tema** | Dark mode obsidian (`#07070B`) com acentos âmbar-apricot (`hsl(24, 88%, 56%)`) |
| **Glass** | Header e categorias com `backdrop-filter: blur(20px)` |
| **Ícones** | 18 SVGs inline Lucide com `stroke-width: 2.2` e `currentColor` |
| **Animações** | Pulse dot, spring transitions, pop-scale, draw-check, fade-slide |
| **Tipografia** | Outfit (Google Fonts) — 8 pesos, antialiased |
| **Scrollbar** | Customizada 6px com brilho na cor primária |

---

## 🔒 Segurança

| Medida | Status | Detalhes |
|--------|--------|---------|
| Validação centralizada no backend | ✅ Ativo | Frontend nunca valida regras de negócio |
| Cálculo de preços server-side | ✅ Ativo | Preços buscados do banco, não do cliente |
| Validação de telefone (Regex BR) | ✅ Ativo | Formato brasileiro rigoroso |
| CORS restrito | ⚠️ Dev | `allow_origins=["*"]` — restringir em produção |
| Rate limiting | 📋 Planejado | Implementar `slowapi` no POST /pedidos |
| Variáveis de ambiente | ✅ Ativo | `.env` no `.gitignore` |

---

## 📝 Documentação Completa

Para detalhes técnicos aprofundados sobre arquitetura, modelagem de dados, fluxo de automação n8n e diretrizes de produção, consulte:

👉 **[Documentação_ Sistema de Pedidos Inteligente.md](Documentação_%20Sistema%20de%20Pedidos%20Inteligente.md)**

---

## 📄 Licença

Este projeto foi desenvolvido para fins de **portfólio profissional** e demonstração de habilidades técnicas em desenvolvimento full-stack.

---

<p align="center">
  Desenvolvido com ☕ e dedicação
</p>
