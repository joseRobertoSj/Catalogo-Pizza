<script setup>
import { ref, onMounted, computed } from 'vue';

const emit = defineEmits(['add-to-cart']);

const produtos = ref([]);
const carregando = ref(true);
const erro = ref(null);
const categoriaAtiva = ref('todos');

const categorias = [
  { id: 'todos', label: 'Tudo' },
  { id: 'pizzas', label: 'Pizzas' },
  { id: 'doces', label: 'Doces' },
  { id: 'bebidas', label: 'Bebidas' }
];

// Buscar produtos do backend FastAPI
const buscarProdutos = async () => {
  try {
    carregando.value = true;
    erro.value = null;
    const apiHost = window.location.hostname || 'localhost';
    const response = await fetch(`http://${apiHost}:8000/produtos`);
    if (!response.ok) {
      throw new Error('Falha ao carregar o catálogo de produtos.');
    }
    const data = await response.json();
    produtos.value = data;
  } catch (err) {
    console.error(err);
    erro.value = 'Não foi possível carregar os produtos. Verifique se o backend está rodando.';
  } finally {
    carregando.value = false;
  }
};

// Filtrar produtos de acordo com a aba selecionada
const produtosFiltrados = computed(() => {
  if (categoriaAtiva.value === 'todos') {
    return produtos.value;
  }
  return produtos.value.filter(p => p.categoria === categoriaAtiva.value);
});

// Formatar moeda em Real (R$)
const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

const adicionarAoCarrinho = (produto) => {
  emit('add-to-cart', produto);
};

onMounted(() => {
  buscarProdutos();
});
</script>

<template>
  <div>
    <!-- Abas de Categorias -->
    <div class="categories">
      <button 
        v-for="cat in categorias" 
        :key="cat.id"
        class="category-tab"
        :class="{ active: categoriaAtiva === cat.id }"
        @click="categoriaAtiva = cat.id"
      >
        <!-- Icon Grid/Tudo (Lucide LayoutGrid) -->
        <svg v-if="cat.id === 'todos'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 15px; height: 15px;">
          <rect width="7" height="7" x="3" y="3" rx="1" />
          <rect width="7" height="7" x="14" y="3" rx="1" />
          <rect width="7" height="7" x="14" y="14" rx="1" />
          <rect width="7" height="7" x="3" y="14" rx="1" />
        </svg>
        
        <!-- Icon Pizza Slice (Lucide Pizza) -->
        <svg v-if="cat.id === 'pizzas'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 15px; height: 15px;">
          <path d="M15 11h.01" />
          <path d="M11 15h.01" />
          <path d="M16 16h.01" />
          <path d="m2 16 20 6-6-20A20 20 0 0 0 2 16Z" />
          <path d="M5.71 17.11a17.04 17.04 0 0 1 11.4-11.4" />
        </svg>
        
        <!-- Icon Cupcake/Doces (Lucide Cupcake) -->
        <svg v-if="cat.id === 'doces'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 15px; height: 15px;">
          <path d="m18 10-.89 7.14A2 2 0 0 1 15.13 19H8.87a2 2 0 0 1-1.98-1.86L6 10" />
          <path d="M18 10a4 4 0 0 0-4-4 1 1 0 0 0-.8.4l-.8.8a1 1 0 0 1-1.6 0l-.8-.8a1 1 0 0 0-.8-.4 4 4 0 0 0-4 4" />
          <circle cx="12" cy="3" r="1" />
          <path d="M12 4v2" />
        </svg>
        
        <!-- Icon Cup/Drink/Bebidas (Lucide CupSoda) -->
        <svg v-if="cat.id === 'bebidas'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 15px; height: 15px;">
          <path d="m6 8 1.75 12A2 2 0 0 0 9.73 21h4.54a2 2 0 0 0 1.98-1.72L18 8" />
          <path d="M5 8h14" />
          <path d="M15 8l-2-5" />
          <path d="M9 8V5a2 2 0 0 1 2-2h1" />
        </svg>
        
        <span>{{ cat.label }}</span>
      </button>
    </div>

    <!-- Catálogo de Cards -->
    <div class="catalog-wrapper">
      <!-- Loading State -->
      <div v-if="carregando" class="loading-container">
        <div class="spinner"></div>
        <p>Carregando cardápio de hoje...</p>
      </div>

      <!-- Error State (Lucide AlertCircle) -->
      <div v-else-if="erro" class="alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 18px; height: 18px; flex-shrink: 0; margin-top: 1px;">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" x2="12" y1="8" y2="12" />
          <line x1="12" x2="12.01" y1="16" y2="16" />
        </svg>
        <span>{{ erro }}</span>
      </div>

      <!-- Empty State (Lucide HelpCircle) -->
      <div v-else-if="produtosFiltrados.length === 0" class="loading-container" style="padding: 60px 20px;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 32px; height: 32px; color: var(--text-muted); margin-bottom: 8px;">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 16v-4" />
          <path d="M12 8h.01" />
        </svg>
        <p>Nenhum produto disponível nesta categoria no momento.</p>
      </div>

      <!-- Listagem de Cards com Transições Fluidas -->
      <transition-group 
        v-else 
        name="list-complete" 
        tag="div" 
        class="catalog"
      >
        <div 
          v-for="produto in produtosFiltrados" 
          :key="produto.id"
          class="product-card"
        >
          <div class="img-container">
            <img :src="produto.url_imagem" :alt="produto.nome" loading="lazy" />
          </div>
          
          <div class="info">
            <div>
              <h3>{{ produto.nome }}</h3>
              <p>{{ produto.descricao }}</p>
            </div>
            <div class="footer">
              <span class="price">{{ formatarMoeda(produto.preco) }}</span>
              <button 
                class="add-btn" 
                @click="adicionarAoCarrinho(produto)"
                aria-label="Adicionar item ao carrinho"
              >
                +
              </button>
            </div>
          </div>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<style scoped>
.list-complete-enter-active,
.list-complete-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.list-complete-enter-from,
.list-complete-leave-to {
  opacity: 0;
  transform: translateY(16px);
}
</style>
