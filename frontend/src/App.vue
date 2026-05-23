<script setup>
import { ref, computed } from 'vue';
import Catalogo from './components/Catalogo.vue';
import CarrinhoFlutuante from './components/CarrinhoFlutuante.vue';
import CheckoutModal from './components/CheckoutModal.vue';
import AdminDashboard from './components/AdminDashboard.vue';

// Estados de Modo Admin e Reatualização
const modoAdmin = ref(false);
const atualizarCatalogoKey = ref(0);

const atualizarCatalogo = () => {
  atualizarCatalogoKey.value++;
};

// Estado global do carrinho
const carrinho = ref([]);
const checkoutAberto = ref(false);

// Métodos de gerenciamento do carrinho
const adicionarAoCarrinho = (produto) => {
  const itemExistente = carrinho.value.find(item => item.produto_id === produto.id);
  
  if (itemExistente) {
    itemExistente.quantidade++;
  } else {
    carrinho.value.push({
      produto_id: produto.id,
      nome: produto.nome,
      preco: Number(produto.preco),
      quantidade: 1
    });
  }
};

const adicionarUnidade = (produtoId) => {
  const item = carrinho.value.find(item => item.produto_id === produtoId);
  if (item) {
    item.quantidade++;
  }
};

const removerUnidade = (produtoId) => {
  const index = carrinho.value.findIndex(item => item.produto_id === produtoId);
  if (index !== -1) {
    const item = carrinho.value[index];
    if (item.quantidade > 1) {
      item.quantidade--;
    } else {
      carrinho.value.splice(index, 1);
    }
  }
};

const limparCarrinho = () => {
  carrinho.value = [];
};

// Computeds
const totalItens = computed(() => {
  return carrinho.value.reduce((acc, item) => acc + item.quantidade, 0);
});

const valorTotal = computed(() => {
  return carrinho.value.reduce((acc, item) => acc + (item.preco * item.quantidade), 0);
});
</script>

<template>
  <div id="app" :class="{ 'admin-layout': modoAdmin }">
    <!-- Header -->
    <header class="header" :class="{ 'header-admin-mode': modoAdmin }">
      <div class="header-top">
        <span class="badge">Aberto para pedidos</span>
        <button class="btn-admin-toggle" @click="modoAdmin = !modoAdmin">
          <svg v-if="!modoAdmin" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-admin">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-admin">
            <rect x="3" y="3" width="7" height="7" />
            <rect x="14" y="3" width="7" height="7" />
            <rect x="14" y="14" width="7" height="7" />
            <rect x="3" y="14" width="7" height="7" />
          </svg>
          <span>{{ modoAdmin ? 'Voltar ao Cardápio' : 'Painel de Gestão' }}</span>
        </button>
      </div>
      <h1>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" />
        </svg>
        <span>Sabor & Arte Delivery</span>
      </h1>
      <p v-if="!modoAdmin">Cardápio inteligente integrado diretamente com a cozinha</p>
    </header>

    <!-- Área Administrativa -->
    <main v-if="modoAdmin" class="app-main">
      <AdminDashboard @atualizar-catalogo="atualizarCatalogo" />
    </main>

    <!-- Área do Cliente (Catálogo de Produtos) -->
    <template v-else>
      <main class="app-main">
        <Catalogo :key="atualizarCatalogoKey" @add-to-cart="adicionarAoCarrinho" />
      </main>

      <!-- Sacola Flutuante na parte inferior -->
      <CarrinhoFlutuante 
        :total-itens="totalItens" 
        :valor-total="valorTotal"
        @abrir-checkout="checkoutAberto = true"
      />

      <!-- Modal de Checkout -->
      <CheckoutModal 
        v-if="checkoutAberto"
        :carrinho="carrinho"
        :valor-total="valorTotal"
        @fechar="checkoutAberto = false"
        @adicionar-unidade="adicionarUnidade"
        @remover-unidade="removerUnidade"
        @limpar-carrinho="limparCarrinho"
      />
    </template>
  </div>
</template>
