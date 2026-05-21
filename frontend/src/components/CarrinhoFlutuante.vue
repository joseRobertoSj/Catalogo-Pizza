<script setup>
defineProps({
  totalItens: {
    type: Number,
    required: true
  },
  valorTotal: {
    type: Number,
    required: true
  }
});

const emit = defineEmits(['abrir-checkout']);

// Formatar moeda em Real (R$)
const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

const prosseguir = () => {
  emit('abrir-checkout');
};
</script>

<template>
  <!-- Exibe a barra apenas se houver pelo menos 1 item adicionado -->
  <transition name="fade-slide">
    <div v-if="totalItens > 0" class="cart-floating-bar">
      <div class="inner">
        <div class="left">
          <div class="cart-icon-container">
            <!-- Ícone Lucide ShoppingBag -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 22px; height: 22px;">
              <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z" />
              <path d="M3 6h18" />
              <path d="M16 10a4 4 0 0 1-8 0" />
            </svg>
            <div class="cart-icon-badge">{{ totalItens }}</div>
          </div>
          
          <div class="price-info">
            <span>Sua Sacola</span>
            <strong>{{ formatarMoeda(valorTotal) }}</strong>
          </div>
        </div>

        <button class="checkout-btn" @click="prosseguir">
          <span>Ver Sacola</span>
          <!-- Seta indicadora Lucide ArrowRight -->
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px;">
            <path d="M5 12h14" />
            <path d="m12 5 7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  </transition>
</template>

<style scoped>
/* Transição suave para a barra flutuante subir de baixo ao aparecer */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translate(-50%, 30px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, 50px);
}
</style>
