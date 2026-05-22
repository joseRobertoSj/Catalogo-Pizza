<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  carrinho: {
    type: Array,
    required: true
  },
  valorTotal: {
    type: Number,
    required: true
  }
});

const emit = defineEmits([
  'fechar',
  'adicionar-unidade',
  'remover-unidade',
  'remover-tudo',
  'limpar-carrinho'
]);

// Estados do formulário
const nomeCliente = ref('');
const telefone = ref('');
const modalidade = ref('entrega'); // 'entrega' ou 'retirada'
const endereco = ref('');
const formaPagamento = ref('PIX');

// Estados de processamento
const enviando = ref(false);
const erroApi = ref(null);
const sucesso = ref(false);
const pedidoIdCriado = ref(null);

// Formatar moeda em Real (R$)
const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

// Fechar modal
const fechar = () => {
  emit('fechar');
};

// Enviar pedido para a API FastAPI
const finalizarPedido = async () => {
  erroApi.value = null;
  sucesso.value = false;
  
  // Mapear carrinho para o schema esperado pelo FastAPI (ItemPedidoSchema)
  const itensSchema = props.carrinho.map(item => ({
    produto_id: item.produto_id,
    quantidade: item.quantidade
  }));

  // Montar payload de envio
  const payload = {
    nome_cliente: nomeCliente.value,
    telefone: telefone.value,
    endereco_entrega: modalidade.value === 'entrega' ? endereco.value : 'Retirada no Estabelecimento',
    forma_pagamento: formaPagamento.value,
    itens: itensSchema
  };

  try {
    enviando.value = true;
    
    const response = await fetch('http://localhost:8000/pedidos', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      // Intercepta erros da API e mostra uma mensagem clara para o cliente.
      // Se for um erro do Pydantic/FastAPI, extraímos a mensagem detalhada do JSON
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          // Erro típico do FastAPI (ValidationError) que retorna uma lista de problemas
          erroApi.value = data.detail.map(d => d.msg).join('; ');
        } else {
          // Erro customizado do HTTPHttpException do FastAPI
          erroApi.value = data.detail;
        }
      } else {
        erroApi.value = 'Ocorreu um erro ao processar o seu pedido. Tente novamente.';
      }
      return;
    }

    // Sucesso absoluto!
    sucesso.value = true;
    pedidoIdCriado.value = data.pedido_id;
    emit('limpar-carrinho');
  } catch (err) {
    console.error(err);
    erroApi.value = 'Conexão com a cozinha falhou! Verifique se a sua API está ativa e tente novamente.';
  } finally {
    enviando.value = false;
  }
};
</script>

<template>
  <div class="modal-overlay" @click.self="fechar">
    <div class="modal-content">
      <!-- Modal Header -->
      <div class="modal-header">
        <h2 style="display: flex; align-items: center; gap: 8px;">
          <!-- Ícone Lucide ShoppingBasket -->
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 20px; height: 20px; color: var(--primary);">
            <path d="M5 11h14" />
            <path d="m5 11 1 9a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-9" />
            <path d="M2.5 7h19" />
            <path d="M10 7V5a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v2" />
          </svg>
          <span>Sua Sacola de Delícias</span>
        </h2>
        <button class="modal-close" @click="fechar" aria-label="Fechar modal" style="display: flex; align-items: center; justify-content: center; padding: 0;">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width: 16px; height: 16px;">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        
        <!-- Estado de Sucesso (Pedido Concluído) -->
        <div v-if="sucesso" class="loading-container success-container" style="padding: 30px 10px; text-align: center;">
          <div class="success-checkmark-circle">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" class="checkmark-icon" style="width: 32px; height: 32px;">
              <path d="M20 6 9 17l-5-5" />
            </svg>
          </div>
          
          <h3 class="success-title" style="display: inline-flex; align-items: center; gap: 8px; justify-content: center;">
            <span>Pedido Confirmado!</span>
            <!-- Ícone Lucide Sparkles para Celebração -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 22px; height: 22px; color: var(--success); filter: drop-shadow(0 0 6px rgba(16, 185, 129, 0.4));">
              <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
              <path d="m5 3 1 2.5L8.5 6 6 7 5 9.5 4 7 1.5 6 4 5.5Z" />
              <path d="m19 17 1 2.5 2.5.5-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1Z" />
            </svg>
          </h3>
          
          <div class="alert-success" style="display: block; margin-bottom: 20px; text-align: left;">
            Seu pedido <strong style="color: #fff; text-shadow: 0 0 8px rgba(255,255,255,0.2);">#{{ pedidoIdCriado }}</strong> foi recebido com sucesso na cozinha e já está sendo preparado pela nossa equipe.
          </div>
          <p style="font-size: 13.5px; color: var(--text-muted); line-height: 1.5; margin-bottom: 28px; max-width: 90%; margin-left: auto; margin-right: auto;">
            Uma notificação completa com o resumo do seu pedido foi enviada diretamente para o seu WhatsApp!
          </p>
          <button class="btn-primary" @click="fechar" style="width: 100%;">
            Voltar para o Cardápio
          </button>
        </div>

        <template v-else>
          <!-- Alerta de Erros do Backend (Conforme Diretriz Crítica de Validação) -->
          <div v-if="erroApi" class="alert-error">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 18px; height: 18px; flex-shrink: 0; margin-top: 1px;">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" x2="12" y1="8" y2="12" />
              <line x1="12" x2="12.01" y1="16" y2="16" />
            </svg>
            <span><strong>Atenção:</strong> {{ erroApi }}</span>
          </div>

          <!-- Listagem dos Itens para Ajustes -->
          <div class="cart-items-list">
            <div v-for="item in carrinho" :key="item.produto_id" class="cart-item">
              <div class="info">
                <span class="name">{{ item.nome }}</span>
                <span class="price">{{ formatarMoeda(item.preco * item.quantidade) }}</span>
              </div>
              <div class="controls">
                <button class="qty-btn" @click="emit('remover-unidade', item.produto_id)" aria-label="Remover unidade">-</button>
                <span class="qty">{{ item.quantidade }}</span>
                <button class="qty-btn" @click="emit('adicionar-unidade', item.produto_id)" aria-label="Adicionar unidade">+</button>
              </div>
            </div>
          </div>

          <!-- Divisor Premium -->
          <div class="divider-glow"></div>

          <!-- Formulário do Cliente -->
          <h3 class="section-title">
            Dados de Entrega
          </h3>

          <div class="form-group">
            <label for="nome">Seu Nome</label>
            <input 
              id="nome"
              type="text" 
              v-model="nomeCliente" 
              placeholder="Ex: João Silva" 
            />
          </div>

          <div class="form-group">
            <label for="telefone">WhatsApp / Celular</label>
            <input 
              id="telefone"
              type="tel" 
              v-model="telefone" 
              placeholder="Ex: (11) 99999-9999" 
            />
          </div>

          <!-- Toggle Entrega/Retirada -->
          <div class="form-group">
            <label>Modalidade</label>
            <div style="display: flex; gap: 8px;">
              <button 
                type="button"
                class="category-tab" 
                :class="{ active: modalidade === 'entrega' }" 
                @click="modalidade = 'entrega'"
                style="flex: 1; padding: 12px; display: flex; align-items: center; justify-content: center; gap: 8px;"
              >
                <!-- Ícone Lucide Bike -->
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 16px; height: 16px;">
                  <circle cx="5.5" cy="17.5" r="2.5" />
                  <circle cx="18.5" cy="17.5" r="2.5" />
                  <path d="M15 6h5v2" />
                  <path d="M12 12h3.5l2.5-5.5" />
                  <path d="M12 12 9.5 7.5H5.5" />
                  <path d="m12 12-3 5.5" />
                </svg>
                <span>Receber em Casa</span>
              </button>
              <button 
                type="button"
                class="category-tab" 
                :class="{ active: modalidade === 'retirada' }" 
                @click="modalidade = 'retirada'"
                style="flex: 1; padding: 12px; display: flex; align-items: center; justify-content: center; gap: 8px;"
              >
                <!-- Ícone Lucide Store -->
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 16px; height: 16px;">
                  <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7" />
                  <path d="M4 12V22a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V12" />
                  <path d="M13 22v-6a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v6" />
                  <path d="M2 12h20" />
                  <path d="M20 7v5" />
                  <path d="M4 7v5" />
                </svg>
                <span>Retirar no Balcão</span>
              </button>
            </div>
          </div>

          <!-- Input do Endereço (Dinâmico dependendo da modalidade) -->
          <transition name="fade-slide-address">
            <div v-if="modalidade === 'entrega'" class="form-group">
              <label for="endereco">Endereço Completo</label>
              <textarea 
                id="endereco"
                v-model="endereco" 
                rows="2" 
                placeholder="Rua, número, bairro, apto (ou referências)..."
              ></textarea>
            </div>
          </transition>

          <!-- Divisor Premium -->
          <div class="divider-glow"></div>

          <!-- Seletor de Pagamento -->
          <h3 class="section-title">
            Forma de Pagamento
          </h3>

          <div class="payment-selector">
            <div 
              class="payment-option" 
              :class="{ active: formaPagamento === 'PIX' }"
              @click="formaPagamento = 'PIX'"
            >
              <!-- Ícone Lucide Zap (PIX) -->
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
              </svg>
              <span>PIX</span>
            </div>

            <div 
              class="payment-option" 
              :class="{ active: formaPagamento === 'Cartão de Crédito/Débito' }"
              @click="formaPagamento = 'Cartão de Crédito/Débito'"
            >
              <!-- Ícone Lucide CreditCard -->
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="20" height="14" x="2" y="5" rx="2" />
                <line x1="2" x2="22" y1="10" y2="10" />
              </svg>
              <span>Cartão</span>
            </div>

            <div 
              class="payment-option" 
              :class="{ active: formaPagamento === 'Dinheiro' }"
              @click="formaPagamento = 'Dinheiro'"
            >
              <!-- Ícone Lucide Banknote (Dinheiro) -->
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="20" height="12" x="2" y="6" rx="2" />
                <circle cx="12" cy="12" r="2" />
                <line x1="6" x2="6.01" y1="12" y2="12" />
                <line x1="18" x2="18.01" y1="12" y2="12" />
              </svg>
              <span>Dinheiro</span>
            </div>
          </div>
        </template>

      </div>

      <!-- Modal Footer (Resumo de Valores e Ação) -->
      <div v-if="!sucesso" class="modal-footer">
        <div class="summary-row">
          <span>Total do Pedido:</span>
          <strong>{{ formatarMoeda(valorTotal) }}</strong>
        </div>

        <button 
          class="btn-primary" 
          @click="finalizarPedido" 
          :disabled="enviando"
        >
          <span v-if="enviando" class="spinner" style="width: 18px; height: 18px; border-width: 2px; margin: 0;"></span>
          <span v-else style="display: flex; align-items: center; gap: 8px;">
            <!-- Ícone Lucide Send (Enviar Pedido) -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="width: 16px; height: 16px;">
              <line x1="22" x2="11" y1="2" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
            <span>Enviar Pedido para Cozinha</span>
          </span>
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Efeito de transição suave de endereço */
.fade-slide-address-enter-active,
.fade-slide-address-leave-active {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-slide-address-enter-from,
.fade-slide-address-leave-to {
  opacity: 0;
  transform: translateY(-10px);
  max-height: 0;
}

/* Divisor Glow Premium */
.divider-glow {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--border) 20%, var(--border) 80%, transparent 100%);
  margin: 24px 0;
  position: relative;
}

.divider-glow::before {
  content: '';
  position: absolute;
  top: 0;
  left: 30%;
  width: 40%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  opacity: 0.15;
}

/* Títulos de Seção do Modal */
.section-title {
  font-size: 13.5px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 16px;
  color: var(--text-heading);
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title::after {
  content: '';
  flex-grow: 1;
  height: 1px;
  background: var(--border);
  opacity: 0.5;
}

/* Checkmark Animado Premium para Sucesso */
.success-checkmark-circle {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.08);
  border: 2px solid rgba(16, 185, 129, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 16px auto 24px;
  color: #10B981;
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.12), inset 0 0 15px rgba(16, 185, 129, 0.05);
  animation: pop-scale 0.55s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

.checkmark-icon {
  width: 34px;
  height: 34px;
  animation: draw-check 0.4s ease-out 0.25s forwards;
  opacity: 0;
  transform: scale(0.8);
}

@keyframes pop-scale {
  0% {
    transform: scale(0.6);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes draw-check {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.success-title {
  font-size: 21px;
  font-weight: 800;
  color: #fff;
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}
</style>
