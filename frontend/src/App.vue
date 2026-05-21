<script setup>
import { ref, computed } from 'vue';
import Catalogo from './components/Catalogo.vue';
import CarrinhoFlutuante from './components/CarrinhoFlutuante.vue';
import CheckoutModal from './components/CheckoutModal.vue';

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
  <div id="app">
    <!-- Header Premium -->
    <header class="header">
      <span class="badge">Aberto para pedidos</span>
      <h1 style="display: flex; align-items: center; gap: 8px; justify-content: center;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 28px; height: 28px; color: var(--primary); filter: drop-shadow(0 0 6px var(--primary-glow-strong));">
          <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" />
        </svg>
        <span>Sabor & Arte Delivery</span>
      </h1>
      <p>Cardápio inteligente integrado diretamente com a cozinha</p>
    </header>

    <!-- Catálogo de Produtos -->
    <main style="flex-grow: 1; display: flex; flex-direction: column;">
      <Catalogo @add-to-cart="adicionarAoCarrinho" />
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
  </div>
</template>
