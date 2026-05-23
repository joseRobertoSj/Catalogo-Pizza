# **Documentação do Projeto: Sistema de Pedidos Inteligente para Micro e Pequenas Empresas**

Esta documentação detalha a concepção, arquitetura e implementação de um **Sistema de Pedidos Online Integrado com WhatsApp e n8n**, projetado especificamente para atender às necessidades de digitalização de micro e pequenos negócios (como pizzarias, docerias, padarias e hamburguerias).

## **1\. A Ideia Geral**

### **O Problema**

Micro e pequenas empresas que operam com entregas locais (delivery) enfrentam gargalos severos no atendimento ao cliente durante horários de pico. Anotar pedidos manualmente pelo WhatsApp consome tempo, gera erros de digitação, confunde a cozinha e afeta a experiência do cliente final. Além disso, plataformas tradicionais de marketplace cobram taxas abusivas por transação, reduzindo a margem de lucro de negócios locais.

### **A Solução**

Um ecossistema ágil de pedidos digitais composto por:

1. **Catálogo Digital Interativo (Frontend Web):** Uma interface rápida, leve e otimizada para dispositivos móveis onde o cliente visualiza o menu, seleciona os itens e realiza o checkout em poucos cliques.  
2. **API de Processamento (Backend):** Um motor robusto e centralizado que gerencia o estado dos produtos, calcula totais, valida regras de negócio e consolida os pedidos de forma segura.  
3. **Fluxo de Automação Low-Code (n8n):** Uma camada de integração que intercepta os pedidos finalizados e gerencia a comunicação em tempo real, automatizando o envio do resumo do pedido formatado diretamente para o WhatsApp do estabelecimento e do cliente.

---

## **2\. Arquitetura Técnica & Stack**

### **Visão Geral da Stack**

| Camada | Tecnologia | Propósito |
|--------|-----------|-----------|
| Frontend | Vue.js 3.5 + Vite 5 | SPA Mobile-First com design premium dark mode |
| Backend | FastAPI (Python) | API REST com validação centralizada |
| Banco de Dados | PostgreSQL (Supabase) | Persistência relacional hospedada na nuvem |
| ORM | SQLAlchemy 2.0 | Mapeamento objeto-relacional |
| Validação | Pydantic v2 | Schemas de entrada com validadores customizados |
| Automação | n8n (Webhook) | Integração com WhatsApp para notificações |
| Tipografia | Google Fonts (Outfit) | Fonte moderna com 8 pesos (300–800) |
| Iconografia | Lucide Icons (SVG inline) | Sistema unificado de ícones vetoriais |

### **Diagrama de Fluxo**

```
[Cliente Mobile]
      │
      ▼
[Vue.js 3 SPA] ──fetch──▶ [FastAPI Backend]
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
              [Validação]  [Cálculo]   [Persistência]
              (Pydantic)   (Seguro)    (Supabase PG)
                                │
                                ▼
                        [Webhook POST]
                                │
                                ▼
                     [n8n Workflow Engine]
                                │
                    ┌───────────┼───────────┐
                    ▼                       ▼
          [WhatsApp Loja]         [WhatsApp Cliente]
```

---

## **3\. Soluções Passo a Passo**

### **Passo 1: O Backend (FastAPI) e Diretrizes de Arquitetura**

O backend funciona como o único ponto de verdade para as regras de negócio. Para garantir um código limpo e de fácil manutenção, a arquitetura segue um isolamento estrito de validações.

#### **Diretriz Crítica de Validação**

* **Centralização Absoluta:** O frontend não executa validações de formulário complexas, de dados cadastrais ou de regras de negócio. Toda e qualquer validação é de responsabilidade estrita da API.  
* **Erros da API:** Se um cliente tentar fechar um pedido com carrinho vazio, formato de telefone inválido ou fora do horário de atendimento, o FastAPI interceptará o fluxo e retornará um erro estruturado. O frontend apenas renderiza a mensagem recebida.  
* **Interface Limpa:** Remova todos os avisos locais, alertas estáticos e mensagens de aviso do código da interface do usuário. Deixe os logs e alertas de processamento restritos às camadas da API e de infraestrutura.

#### **Principais Endpoints (FastAPI)**

* `GET /` — Status da API e link para documentação Swagger.
* `GET /produtos` — Retorna a lista de itens ativos no catálogo. Suporta filtro por categoria via Query Parameter (`?categoria=pizzas`).
* `GET /produtos/{produto_id}` — Retorna os detalhes de um item específico.
* `POST /pedidos` — Recebe os dados de checkout, processa a validação das regras de negócio, persiste no banco de dados e aciona o Webhook da automação.

#### **Exemplo: Schema de Validação (Pydantic v2)**

```python
import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class ItemPedidoSchema(BaseModel):
    produto_id: int
    quantidade: int = Field(..., gt=0, description="A quantidade deve ser maior que 0")

class PedidoCreateSchema(BaseModel):
    nome_cliente: str = Field(..., min_length=2, description="O nome deve conter pelo menos 2 caracteres")
    telefone: str = Field(..., description="Telefone de contato do cliente")
    endereco_entrega: Optional[str] = None
    forma_pagamento: str = Field(..., description="Forma de pagamento (ex: PIX, Cartão, Dinheiro)")
    itens: List[ItemPedidoSchema] = Field(..., min_length=1, description="O carrinho deve conter pelo menos 1 item")

    @field_validator('telefone')
    @classmethod
    def validar_telefone_br(cls, v: str) -> str:
        padrao = r'^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$'
        if not re.match(padrao, v):
            raise ValueError('O número de telefone informado é inválido. Use um formato válido (ex: 11999999999).')
        return v
```

#### **Segurança no Cálculo de Preços**

O preço de cada item é **sempre recuperado diretamente do banco de dados** no momento do checkout. Nunca se confia no valor enviado pelo frontend para evitar fraudes ou adulterações no payload JSON:

```python
for item in pedido_data.itens:
    produto = db.query(models.Produto).filter(
        models.Produto.id == item.produto_id,
        models.Produto.ativo == True
    ).first()
    
    subtotal_item = produto.preco * item.quantidade
    total_acumulado += subtotal_item
```

### **Passo 2: O Banco de Dados Relacional (PostgreSQL)**

O armazenamento dos dados é estruturado para garantir integridade referencial, velocidade nas consultas e histórico limpo para futuras análises de vendas ou faturamento do comércio.

#### **Modelagem de Dados (MER)**

1. **Tabela: produtos**  
   * `id` (SERIAL, Chave Primária)  
   * `nome` (VARCHAR(100), Não Nulo)  
   * `descricao` (TEXT)  
   * `preco` (NUMERIC(10, 2), Não Nulo)  
   * `categoria` (VARCHAR(50)) → Ex: `'pizzas'`, `'doces'`, `'bebidas'`  
   * `url_imagem` (VARCHAR(255))  
   * `ativo` (BOOLEAN, Default True)  

2. **Tabela: pedidos**  
   * `id` (SERIAL, Chave Primária)  
   * `nome_cliente` (VARCHAR(150), Não Nulo)  
   * `telefone` (VARCHAR(20), Não Nulo)  
   * `endereco_entrega` (TEXT, Opcional se for retirada)  
   * `forma_pagamento` (VARCHAR(50), Não Nulo)  
   * `total` (NUMERIC(10,2), Não Nulo)  
   * `criado_em` (TIMESTAMP WITH TZ, Default `CURRENT_TIMESTAMP`)  
   * `status` (VARCHAR(30)) → Ex: `'recebido'`, `'em_preparacao'`, `'enviado'`, `'entregue'`  

3. **Tabela: itens\_pedido**  
   * `id` (SERIAL, Chave Primária)  
   * `pedido_id` (INTEGER, FK → pedidos(id) ON DELETE CASCADE)  
   * `produto_id` (INTEGER, FK → produtos(id))  
   * `quantidade` (INTEGER, Não Nulo)  
   * `preco_unitario` (NUMERIC(10,2), Não Nulo)

#### **Relacionamentos ORM (SQLAlchemy)**

```python
# Pedido → Itens (Um para Muitos, com deleção em cascata)
itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

# ItemPedido → Produto (Muitos para Um)
produto = relationship("Produto")
```

### **Passo 3: A Interface do Usuário (Vue.js 3 + Vite)**

O frontend é construído sob a premissa de máxima velocidade e foco total na experiência em smartphones (*Mobile-First*), com um design premium dark mode que transmite sofisticação e confiança.

#### **Características da Interface**

* **Consumo Assíncrono:** A aplicação consome a API do FastAPI via `fetch()` nativo, sem dependências externas como Axios.
* **Zero Lógica de Validação Local:** Campos como nome, telefone e itens do carrinho não possuem tratamento de strings ou regras rígidas no frontend. Ao enviar o formulário, caso ocorra alguma inconsistência, o Vue.js captura o status do erro HTTP (como `400 Bad Request` ou `422 Unprocessable Entity`), lê o campo `detail` do JSON enviado pelo backend e renderiza dinamicamente na tela para o usuário.
* **Zero Dependências Extras:** O frontend utiliza apenas Vue 3 como dependência de produção. Nenhuma biblioteca de UI, ícones ou CSS framework é necessária — tudo é artesanal.

#### **Componentização**

| Componente | Responsabilidade |
|-----------|-----------------|
| `App.vue` | Layout raiz, header com logo, gerenciamento global do estado do carrinho (ref reativo), coordenação de eventos entre componentes |
| `Catalogo.vue` | Busca e renderiza os cards de produtos divididos por abas de categorias filtráveis, com estados de loading, erro e vazio |
| `CarrinhoFlutuante.vue` | Barra flutuante fixa no rodapé que exibe quantidade e valor total, com animação de entrada/saída suave |
| `CheckoutModal.vue` | Bottom-sheet modal com formulário de dados de entrega/retirada, seletor de pagamento, e tela de confirmação de sucesso animada |

#### **Gerenciamento de Estado**

O estado do carrinho é gerenciado centralmente no `App.vue` usando `ref()` e `computed()` do Vue 3 Composition API, e propagado via props e eventos customizados:

```
App.vue (carrinho, totalItens, valorTotal)
   │
   ├── @add-to-cart ←── Catalogo.vue
   │
   ├── :total-itens, :valor-total ──→ CarrinhoFlutuante.vue
   │       └── @abrir-checkout ──→ checkoutAberto = true
   │
   └── :carrinho, :valor-total ──→ CheckoutModal.vue
           ├── @adicionar-unidade
           ├── @remover-unidade
           ├── @limpar-carrinho
           └── @fechar
```

### **Passo 4: Automação de Fluxo e Mensageria (n8n & Discord)**

A integração nativa com o **n8n** e canais de comunicação em tempo real (como **Discord Webhook** e WhatsApp) elimina a necessidade de o comerciante gerenciar múltiplos painéis complexos durante a correria operacional. As notificações chegam instantaneamente na cozinha e no canal da gerência assim que um cliente finaliza um pedido.

#### **Arquitetura Assíncrona via FastAPI (Background Tasks)**

Para garantir uma experiência de compra instantânea e sem travamentos no checkout do frontend (onde lentidões ou falhas na rede externa poderiam travar o navegador do cliente), a API do backend dispara a automação do n8n de forma assíncrona:

1. O backend processa as validações de estoque, calcula os preços reais do banco e salva o pedido no Supabase.
2. O FastAPI responde instantaneamente `HTTP 201 Created` para o cliente Vue.js.
3. O envio do payload para o n8n é agendado em segundo plano usando `BackgroundTasks` da biblioteca nativa do FastAPI, processando a requisição de forma resiliente com tratamento de erros isolado e `timeout` seguro.

#### **Arquitetura do Workflow no n8n**

1. **Nó de Entrada (Webhook Trigger):** Escuta requisições do tipo POST no caminho `/webhook/novo-pedido`. Ele é configurado com a opção *Respond: Immediately* para liberar a API do backend instantaneamente com um status HTTP 200, processando o fluxo subsequente de forma autônoma.
2. **Nó de Formatação Inteligente (Code Node - JS):** Recebe o JSON. Como os dados de envio POST no n8n vêm aninhados dentro de um objeto chamado `body`, o nó executa um script JavaScript blindado que extrai com segurança os dados de dentro de `body`, mapeia os itens do carrinho e gera uma mensagem elegante em Markdown pronta para leitura.
3. **Nó de Envio do Discord (Discord Webhook):** Conecta-se diretamente ao canal da pizzaria no Discord através do Webhook oficial, enviando o conteúdo da mensagem formatada no campo `content` usando expressões nativas do n8n.

#### **Código JavaScript de Formatação Blindado (Code Node)**

Este script de processamento foi desenhado para ser 100% resiliente, evitando falhas de propriedades não definidas (`Cannot read properties of undefined`) mesmo se o n8n sofrer mudanças de versão (`$input.all()` vs `items`) ou se algum dado opcional do pedido for omitido:

```javascript
// 1. Captura os dados brutos de entrada compatível com n8n moderno e legado
let dadosBrutos = null;
if (typeof $json !== 'undefined') {
  dadosBrutos = $json;
} else if (typeof $input !== 'undefined' && $input.all().length > 0) {
  dadosBrutos = $input.all()[0].json;
} else if (typeof items !== 'undefined' && items.length > 0) {
  dadosBrutos = items[0].json;
}

if (!dadosBrutos) {
  throw new Error("Não foi possível encontrar os dados da entrada.");
}

// 2. Extração inteligente do corpo do Webhook (POST body)
const pedido = dadosBrutos.body ? dadosBrutos.body : dadosBrutos;

// 3. Garante que os itens sejam tratados sempre como lista
const itens = Array.isArray(pedido.itens) ? pedido.itens : [];

// 4. Formata o resumo do carrinho com preços formatados para real (R$)
const itensFormatados = itens.map(item => {
  const quant = item.quantidade || 1;
  const preco = item.preco_unitario || item.preco || 0;
  const prod = item.produto || item.nome || 'Produto';
  return `• ${quant}x ${prod} - R$ ${(preco * quant).toFixed(2).replace('.', ',')}`;
}).join('\n') || '• Nenhum item informado';

// 5. Detecta dinamicamente a modalidade (Entrega em casa vs Balcão)
const enderecoFormatado = pedido.endereco 
  ? `📍 **Endereço:** ${pedido.endereco}`
  : `🛵 **Modalidade:** Retirada no Balcão`;

// 6. Constrói a mensagem visual em Markdown premium para o Discord
const mensagem = `🚨 **NOVO PEDIDO RECEBIDO!** 🚨\n\n` +
  `👤 **Cliente:** ${pedido.cliente || pedido.nome_cliente || 'Desconhecido'}\n` +
  `📞 **Contato:** ${pedido.telefone || 'Não informado'}\n` +
  `${enderecoFormatado}\n\n` +
  `----------------------------------\n` +
  `📋 **Resumo do Pedido:**\n` +
  `${itensFormatados}\n` +
  `----------------------------------\n\n` +
  `💰 **Total do Pedido:** R$ ${Number(pedido.total || 0).toFixed(2).replace('.', ',')}\n` +
  `💳 **Forma de Pagamento:** ${pedido.forma_pagamento || 'Não informada'}\n\n` +
  `🛵 **Status:** Aguardando confirmação da cozinha.`;

return [{ json: { mensagem } }];
```

#### **Payload do Webhook (Estrutura JSON)**

```json
{
  "pedido_id": 42,
  "cliente": "João Silva",
  "telefone": "11999999999",
  "endereco": "Rua das Flores, 123 - Apto 42",
  "forma_pagamento": "PIX",
  "total": 101.00,
  "status": "recebido",
  "itens": [
    {
      "produto": "Pizza Calabresa Gourmet",
      "quantidade": 2,
      "preco_unitario": 45.00
    },
    {
      "produto": "Coca-Cola 2L Gelada",
      "quantidade": 1,
      "preco_unitario": 11.00
    }
  ]
}
```

#### **Visual da Notificação Recebida no Discord:**

```text
🚨 NOVO PEDIDO RECEBIDO! 🚨

👤 Cliente: João Silva
📞 Contato: 11999999999
📍 Endereço: Rua das Flores, 123 - Apto 42

----------------------------------
📋 Resumo do Pedido:
• 2x Pizza Calabresa Gourmet - R$ 90,00
• 1x Coca-Cola 2L Gelada - R$ 11,00
----------------------------------

💰 Total do Pedido: R$ 101,00
💳 Forma de Pagamento: PIX

🛵 Status: Aguardando confirmação da cozinha.
```

---

## **4\. Status da Implementação Realizada**

### **4.1. Estrutura de Diretórios**

```text
Portifolio FOREVER/
├── .gitignore
├── Documentação_ Sistema de Pedidos Inteligente.md
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app, CORS, rotas, seed de dados
│   │   ├── database.py      # Engine SQLAlchemy + sessão com Supabase (.env)
│   │   ├── models.py        # Tabelas ORM (produtos, pedidos, itens_pedido)
│   │   └── schemas.py       # Schemas Pydantic v2 com validators
│   ├── .env                 # DATABASE_URL do Supabase (não versionado)
│   └── requirements.txt     # Dependências Python
│
└── frontend/
    ├── package.json          # Vue 3.5 + Vite 5
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.js           # Bootstrap da app Vue
        ├── style.css         # Design System Premium (923 linhas de CSS puro)
        ├── App.vue           # Layout raiz + estado do carrinho
        └── components/
            ├── Catalogo.vue          # Cards de produtos + filtro por categorias
            ├── CarrinhoFlutuante.vue  # Barra flutuante do carrinho
            └── CheckoutModal.vue      # Modal de checkout completo
```

### **4.2. Backend — Implementação Completa**

#### **Banco de Dados (Supabase — PostgreSQL)**

* **Integração:** Conexão configurada no `.env` com `DATABASE_URL` oficial do Supabase.
* **Criação Automática:** No boot, `Base.metadata.create_all(bind=engine)` cria todas as tabelas automaticamente.
* **Seed de Dados:** Ao detectar banco vazio, a API pré-cadastra 6 produtos premium (2 pizzas, 2 doces, 2 bebidas) com fotos profissionais do Unsplash.

#### **Dependências Python (`requirements.txt`)**

| Pacote | Versão Mínima | Função |
|--------|--------------|--------|
| `fastapi` | ≥ 0.110.0 | Framework web assíncrono |
| `uvicorn` | ≥ 0.28.0 | Servidor ASGI de alta performance |
| `sqlalchemy` | ≥ 2.0.28 | ORM para mapeamento de tabelas |
| `psycopg2-binary` | ≥ 2.9.9 | Driver PostgreSQL nativo |
| `pydantic` | ≥ 2.6.4 | Validação de schemas e serialização |
| `python-dotenv` | ≥ 1.0.1 | Carregamento de variáveis `.env` |
| `requests` | ≥ 2.31.0 | Chamadas HTTP para webhooks |

#### **Rotas Ativas & Funcionais**

* **`GET /`** — Status da API com link para `/docs`.
* **`GET /produtos`** — Lista produtos ativos. Filtro opcional: `?categoria=pizzas`.
* **`GET /produtos/{produto_id}`** — Detalhes de um produto.
* **`POST /pedidos`** — Checkout completo:
  * Validação de carrinho vazio
  * Validação de telefone brasileiro (Regex)
  * Cálculo seguro do total (preços do banco, não do cliente)
  * Persistência com relacionamentos
  * Payload de webhook preparado para disparo ao n8n

### **4.3. Frontend — Implementação Completa**

#### **Dependências (`package.json`)**

| Pacote | Versão | Tipo |
|--------|--------|------|
| `vue` | ^3.5.34 | Produção |
| `@vitejs/plugin-vue` | ^5.0.4 | Desenvolvimento |
| `vite` | ^5.4.1 | Desenvolvimento |

#### **Design System Premium Dark Mode**

A identidade visual segue uma estética gourmet sofisticada com design obsidian escuro e acentos âmbar-apricot quentes. Todos os tokens estão centralizados em variáveis CSS no arquivo `style.css`:

| Token CSS | Valor | Uso |
|-----------|-------|-----|
| `--primary` | `hsl(24, 88%, 56%)` | Cor âmbar-apricot gourmet principal |
| `--primary-hover` | `hsl(24, 88%, 48%)` | Estado hover dos botões |
| `--primary-glow` | `rgba(240, 105, 30, 0.10)` | Brilho suave para sombras |
| `--bg` | `#07070B` | Fundo obsidian preto absoluto |
| `--surface` | `#12121A` | Superfícies elevadas |
| `--surface-card` | `#14141E` | Cards de produtos |
| `--text` | `#C5C6D0` | Texto principal |
| `--text-muted` | `#8E909F` | Texto secundário |
| `--text-heading` | `#FFFFFF` | Títulos e headings |
| `--success` | `#10B981` | Feedback positivo (verde esmeralda) |
| `--error` | `#EF4444` | Feedback de erro |

**Técnicas visuais utilizadas:**

* **Glassmorphism:** Header sticky e barra de categorias com `backdrop-filter: blur(20px)` e fundo translúcido.
* **Micro-animações:** Pulse dot no badge "Aberto para pedidos", rotação do botão `+`, spring transitions nos cards, animação pop-scale no checkmark de sucesso.
* **Gradientes sutis:** Background com halos radiais `rgba(240, 105, 30, 0.02)` nas extremidades.
* **Scrollbar customizada:** Thumb de 6px com hover que brilha na cor primária.

#### **Sistema de Iconografia: Lucide Inline SVG**

Toda a iconografia da aplicação utiliza **SVGs inline do estilo Lucide** com os seguintes parâmetros unificados:

| Parâmetro | Valor | Propósito |
|-----------|-------|-----------|
| `stroke-width` | `2.2` | Traço fino e elegante |
| `stroke-linecap` | `round` | Pontas arredondadas |
| `stroke-linejoin` | `round` | Junções suaves |
| `fill` | `none` | Estilo outline puro |
| `stroke` | `currentColor` | Herda a cor do contexto CSS |

**Mapeamento completo de ícones:**

| Contexto | Ícone Lucide | Componente |
|----------|-------------|-----------|
| Logo do app | `Flame` (chama) | App.vue |
| Categoria "Tudo" | `LayoutGrid` (4 quadrados) | Catalogo.vue |
| Categoria "Pizzas" | `Pizza` (fatia) | Catalogo.vue |
| Categoria "Doces" | `Cake` (cupcake com cereja) | Catalogo.vue |
| Categoria "Bebidas" | `CupSoda` (copo com canudo) | Catalogo.vue |
| Estado de erro | `AlertCircle` (alerta circular) | Catalogo.vue / CheckoutModal.vue |
| Estado vazio | `Info` (informação circular) | Catalogo.vue |
| Carrinho flutuante | `ShoppingBag` (sacola) | CarrinhoFlutuante.vue |
| Seta do botão | `ArrowRight` | CarrinhoFlutuante.vue |
| Título do checkout | `ShoppingBasket` (cesta) | CheckoutModal.vue |
| Fechar modal | `X` (cruz fina) | CheckoutModal.vue |
| Entrega | `Bike` (bicicleta/moto) | CheckoutModal.vue |
| Retirada | `Store` (loja) | CheckoutModal.vue |
| PIX | `Zap` (raio elétrico) | CheckoutModal.vue |
| Cartão | `CreditCard` | CheckoutModal.vue |
| Dinheiro | `Banknote` (cédula) | CheckoutModal.vue |
| Enviar pedido | `Send` (avião de papel) | CheckoutModal.vue |
| Sucesso | `Check` (marca de verificação) | CheckoutModal.vue |
| Celebração | `Sparkles` (brilhos) | CheckoutModal.vue |

> **Nota:** Os ícones são renderizados como SVGs inline diretamente nos templates Vue — sem bibliotecas npm de ícones — garantindo zero overhead de bundle e controle pixel-perfect.

#### **Componentes — Detalhamento Funcional**

**`Catalogo.vue`**

* Busca produtos da API com `fetch('http://localhost:8000/produtos')` no `onMounted`.
* Filtro local por categoria via `computed` (`produtosFiltrados`).
* Cards com imagem lazy-loaded, efeito de zoom no hover (scale 1.12), e truncagem inteligente de descrição (`-webkit-line-clamp: 2`).
* Transições de entrada/saída com `<transition-group>` usando curva `cubic-bezier(0.16, 1, 0.3, 1)`.

**`CarrinhoFlutuante.vue`**

* Barra fixa posicionada na parte inferior com gradiente de fade.
* Badge de quantidade sobre o ícone da sacola.
* Botão "Ver Sacola" com animação pulsante (`pulse-ring`) para chamar atenção.
* Transição `fade-slide` para entrar e sair suavemente.

**`CheckoutModal.vue`**

* Bottom-sheet estilo nativo mobile, animado de baixo para cima (`slide-up-modal`).
* Listagem dos itens com botões `+`/`-` para ajuste de quantidade em tempo real.
* Toggle `Receber em Casa` / `Retirar no Balcão` com ícones de Bike e Store.
* Campo de endereço exibido condicionalmente com transição suave (`fade-slide-address`).
* Seletor de pagamento em grid 3 colunas: PIX, Cartão e Dinheiro com ícones e estados ativos com borda brilhante.
* Tela de confirmação de sucesso com checkmark animado (pop-scale + draw-check) e ícone Sparkles.
* Interceptação completa de erros HTTP do backend com renderização dinâmica da mensagem.

---

## **5\. Benefícios Estratégicos para o Portfólio**

Apresentar este projeto estruturado dessa forma no seu portfólio demonstra habilidades essenciais valorizadas no mercado:

* **Foco no Cliente Final:** Prova que você entende de regras de negócios locais e resolve problemas que afetam o faturamento da empresa.  
* **Arquitetura de Alta Performance:** A descentralização de interfaces e a centralização estrita de regras e mensagens no backend refletem maturidade no desenvolvimento de software comercial e facilidade de escala.  
* **Design System Próprio:** A construção de um design system completo em CSS puro (923 linhas), sem frameworks de UI, demonstra domínio profundo de CSS moderno, variáveis customizadas, glassmorphism, micro-animações e responsividade.
* **Iconografia Vetorial Artesanal:** A implementação de um sistema unificado de ícones Lucide inline, sem dependências npm, demonstra atenção ao detalhe e performance.
* **Agilidade com Automações:** O uso inteligente do n8n demonstra que você sabe integrar ferramentas modernas para entregar valor rapidamente sem a necessidade de reinventar a roda na camada de mensageria.

---

## **6\. Como Rodar o Projeto Localmente**

### **6.1. Backend**

```bash
# 1. Navegue até a pasta do backend
cd backend

# 2. Instale as dependências Python
pip install -r requirements.txt

# 3. Configure o arquivo .env com sua DATABASE_URL do Supabase
# DATABASE_URL=postgresql://user:password@host:port/database

# 4. Inicie o servidor FastAPI
python -m uvicorn app.main:app --reload
```

* **API:** <http://127.0.0.1:8000>
* **Documentação Swagger Interativa:** <http://127.0.0.1:8000/docs>

### **6.2. Frontend**

```bash
# 1. Navegue até a pasta do frontend
cd frontend

# 2. Instale as dependências Node.js
npm install

# 3. Inicie o servidor de desenvolvimento Vite
npm run dev
```

* **Aplicação:** <http://localhost:5173>

> **Importante:** O backend precisa estar rodando antes de acessar o frontend, pois o catálogo é carregado via API.

---

## **7\. Diretrizes de Cibersegurança para Produção**

Para realizar a transição do ambiente de portfólio/desenvolvimento local para um ambiente de **produção comercial real**, as seguintes medidas de segurança devem ser ativadas:

### **7.1. Restrição de Origens no CORS**

* **Situação Atual:** A API está configurada com `allow_origins=["*"]` no arquivo `main.py` para facilitar os testes locais.
* **Medida de Segurança:** Ao publicar o frontend (ex: na Vercel ou Netlify), deve-se alterar essa configuração para aceitar apenas o domínio oficial da aplicação:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sua-url-do-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **7.2. Prevenção de Abuso e Spam (Rate Limiting)**

* **Situação Atual:** O endpoint `POST /pedidos` está totalmente aberto, aceitando requisições ilimitadas para testes.
* **Medida de Segurança:** Implementar um limitador de requisições por IP (como a biblioteca `slowapi` no FastAPI) para limitar chamadas a endpoints críticos de escrita:

```python
# Exemplo de limitação de taxa
# @app.post("/pedidos")
# @limiter.limit("3/minute")
```

### **7.3. Variáveis de Ambiente**

* O arquivo `.env` contém credenciais sensíveis do Supabase e as chaves de integração do n8n (`N8N_WEBHOOK_URL`, `N8N_WEBHOOK_USER`, `N8N_WEBHOOK_PASSWORD`), estando devidamente listado no `.gitignore` para proteção das credenciais.
* Em produção, utilizar variáveis de ambiente do servidor (Render, Railway, Heroku) ao invés do arquivo `.env`.

### **7.4. URL da API em Produção**

* **Situação Atual:** O frontend aponta para `http://localhost:8000` hardcoded nos componentes.
* **Medida de Segurança:** Em produção, utilizar variáveis de ambiente do Vite (`import.meta.env.VITE_API_URL`) para configurar a URL da API dinamicamente.
