# Sistema de Pedidos Inteligente — Frontend Web

Interface mobile-first premium do **Sistema de Pedidos Inteligente**, construída com **Vue.js 3** (Composition API) e compilada com **Vite 5**. Design system artesanal em CSS puro com dark mode obsidian e acentos âmbar gourmet.

---

## Stack & Dependências

| Pacote | Versão | Tipo |
|--------|--------|------|
| `vue` | ^3.5.34 | Produção |
| `@vitejs/plugin-vue` | ^5.0.4 | Desenvolvimento |
| `vite` | ^5.4.1 | Desenvolvimento |

> **Zero bibliotecas extras.** Sem Axios, sem frameworks CSS, sem bibliotecas de ícones. Tudo artesanal.

---

## Estrutura de Diretórios

```text
frontend/
├── src/
│   ├── components/
│   │   ├── Catalogo.vue            # Cards de produtos com filtro por categorias
│   │   ├── CarrinhoFlutuante.vue   # Barra flutuante inferior com sacola e total
│   │   └── CheckoutModal.vue       # Bottom-sheet: formulário + pagamento + confirmação
│   ├── App.vue                     # Layout raiz, header, estado global do carrinho
│   ├── main.js                     # Bootstrap da aplicação Vue
│   └── style.css                   # Design System completo (923 linhas de CSS puro)
├── index.html                      # Template HTML base
├── vite.config.js                  # Configuração do bundler Vite
└── package.json                    # Dependências e scripts npm
```

---

## Design System Premium

### Paleta de Cores (Dark Mode Obsidian & Amber)

| Token | Valor | Uso |
|-------|-------|-----|
| `--primary` | `hsl(24, 88%, 56%)` | Âmbar-apricot gourmet |
| `--bg` | `#07070B` | Fundo obsidian absoluto |
| `--surface` | `#12121A` | Superfícies elevadas |
| `--surface-card` | `#14141E` | Cards de produto |
| `--text` | `#C5C6D0` | Texto legível |
| `--text-heading` | `#FFFFFF` | Títulos |
| `--success` | `#10B981` | Confirmação (verde esmeralda) |
| `--error` | `#EF4444` | Erros |

### Tipografia
- **Fonte:** Outfit (Google Fonts) — pesos 300 a 800
- **Rendering:** `-webkit-font-smoothing: antialiased`

### Técnicas Visuais
- **Glassmorphism:** Header e categorias com `backdrop-filter: blur(20px)`
- **Micro-animações:** Pulse dot, rotação do botão +, spring transitions, pop-scale no checkmark
- **Gradientes sutis:** Halos radiais âmbar nas extremidades do fundo
- **Scrollbar customizada:** 6px com brilho na cor primária ao hover

### Iconografia — Lucide Inline SVG

Todos os ícones são SVGs inline no estilo **Lucide** com parâmetros unificados:
- `stroke-width: 2.2` | `stroke-linecap: round` | `fill: none` | `stroke: currentColor`

| Contexto | Ícone |
|----------|-------|
| Logo | Flame |
| Categoria "Tudo" | LayoutGrid |
| Categoria "Pizzas" | Pizza |
| Categoria "Doces" | Cake (cupcake) |
| Categoria "Bebidas" | CupSoda |
| Carrinho | ShoppingBag |
| Checkout | ShoppingBasket |
| Fechar | X |
| Entrega | Bike |
| Retirada | Store |
| PIX | Zap |
| Cartão | CreditCard |
| Dinheiro | Banknote |
| Enviar | Send |
| Sucesso | Check + Sparkles |
| Erro | AlertCircle |

---

## Componentes

### `App.vue`
- Header com logo Flame, badge "Aberto para pedidos" com dot pulsante
- Estado reativo do carrinho via `ref()` e `computed()`
- Coordenação de eventos entre todos os componentes filhos

### `Catalogo.vue`
- Busca assíncrona da API via `fetch()` no `onMounted`
- Filtro por categorias com segmented control estilo iOS (glassmorphism)
- Cards com imagem lazy-loaded, zoom no hover (scale 1.12), truncagem de texto
- Estados: loading (spinner), erro (AlertCircle), vazio (Info)
- `<transition-group>` com curva spring para animações de entrada/saída

### `CarrinhoFlutuante.vue`
- Barra fixa no rodapé com gradiente de fade
- Ícone ShoppingBag com badge de quantidade
- Botão "Ver Sacola" com animação pulsante `pulse-ring`
- Transição `fade-slide` para aparecer/desaparecer suavemente

### `CheckoutModal.vue`
- Bottom-sheet animado de baixo para cima (estilo nativo mobile)
- Lista de itens com `+`/`-` para ajuste de quantidade
- Toggle Entrega/Retirada com ícones Bike e Store
- Campo de endereço condicional com transição suave
- Seletor de pagamento 3 colunas: PIX, Cartão, Dinheiro
- Confirmação de sucesso com checkmark animado (pop-scale + draw-check)
- Interceptação de erros HTTP do backend com renderização dinâmica

---

## Como Executar Localmente

### Pré-requisitos
- **Node.js 20+** instalado

### Instalação e Execução

```bash
# Navegue até a pasta do frontend
cd frontend

# Instale as dependências
npm install

# Inicie o servidor de desenvolvimento
npm run dev
```

- **Aplicação:** http://localhost:5173

### Build de Produção

```bash
npm run build
npm run preview
```

---

## Integração com o Backend

A aplicação consome a API FastAPI em `http://localhost:8000`.

| Componente | Endpoint Consumido | Método |
|-----------|-------------------|--------|
| `Catalogo.vue` | `/produtos` | GET |
| `CheckoutModal.vue` | `/pedidos` | POST |

> **Importante:** O backend deve estar rodando antes de acessar o frontend.

### Para Produção
Substituir a URL hardcoded por variável de ambiente Vite:
```javascript
// Usar: import.meta.env.VITE_API_URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```
