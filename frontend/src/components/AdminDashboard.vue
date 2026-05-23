<script setup>
import { ref, onMounted, computed } from 'vue';

const emit = defineEmits(['atualizar-catalogo']);

// Estados de Autenticação
const chaveAdminInput = ref('');
const autenticado = ref(false);
const erroLogin = ref('');

// Estados de Produtos
const produtos = ref([]);
const carregando = ref(false);
const erro = ref(null);

// Chave/Token padrão de autenticação com o Backend
const ADMIN_TOKEN = 'sabor-arte-admin-secreto';

// Base da API dinâmica para rodar em computadores ou celulares locais
const apiHost = window.location.hostname || 'localhost';
const API_BASE = `http://${apiHost}:8000`;

// Estado do Modal de Formulário
const modalAberto = ref(false);
const editandoId = ref(null);

const form = ref({
  nome: '',
  descricao: '',
  preco: '',
  categoria: 'pizzas',
  url_imagem: '',
  ativo: true
});

const erroForm = ref('');
const salvando = ref(false);

// Métodos de Autenticação
const realizarLogin = () => {
  if (chaveAdminInput.value === 'admin') {
    autenticado.value = true;
    erroLogin.value = '';
    buscarProdutos();
  } else {
    erroLogin.value = 'Chave administrativa incorreta! Tente "admin".';
  }
};

// Buscar todos os produtos (incluindo inativos) do backend
const buscarProdutos = async () => {
  try {
    carregando.value = true;
    erro.value = null;
    
    // Passa o header de segurança exigido pela API
    const response = await fetch(`${API_BASE}/admin/produtos`, {
      headers: {
        'X-Admin-Token': ADMIN_TOKEN
      }
    });

    if (response.status === 401) {
      throw new Error('Não autorizado! A chave de API do backend está inválida.');
    }

    if (!response.ok) {
      throw new Error('Falha ao buscar os produtos no banco de dados.');
    }

    produtos.value = await response.json();
  } catch (err) {
    console.error(err);
    erro.value = err.message;
  } finally {
    carregando.value = false;
  }
};

// Alternar o status de ativo/inativo instantaneamente
const alternarAtivo = async (produto) => {
  try {
    const novoStatus = !produto.ativo;
    
    const response = await fetch(`${API_BASE}/produtos/${produto.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Token': ADMIN_TOKEN
      },
      body: JSON.stringify({
        ativo: novoStatus
      })
    });

    if (!response.ok) {
      throw new Error('Erro ao atualizar status do produto.');
    }

    produto.ativo = novoStatus;
    emit('atualizar-catalogo');
  } catch (err) {
    alert(err.message);
  }
};

// Abrir modal de cadastro
const abrirNovoModal = () => {
  editandoId.value = null;
  form.value = {
    nome: '',
    descricao: '',
    preco: '',
    categoria: 'pizzas',
    url_imagem: '',
    ativo: true
  };
  erroForm.value = '';
  modalAberto.value = true;
};

// Abrir modal de edição com dados carregados
const abrirEditarModal = (produto) => {
  editandoId.value = produto.id;
  form.value = {
    nome: produto.nome,
    descricao: produto.descricao || '',
    preco: produto.preco,
    categoria: produto.categoria || 'pizzas',
    url_imagem: produto.url_imagem || '',
    ativo: produto.ativo
  };
  erroForm.value = '';
  modalAberto.value = true;
};

// Enviar Formulário (Salvar / Atualizar)
const salvarProduto = async () => {
  if (!form.value.nome || !form.value.preco) {
    erroForm.value = 'Nome e Preço são campos obrigatórios!';
    return;
  }

  try {
    salvando.value = true;
    erroForm.value = '';

    const url = editandoId.value 
      ? `${API_BASE}/produtos/${editandoId.value}`
      : `${API_BASE}/produtos`;
    
    const method = editandoId.value ? 'PUT' : 'POST';

    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Token': ADMIN_TOKEN
      },
      body: JSON.stringify({
        nome: form.value.nome,
        descricao: form.value.descricao || null,
        preco: Number(form.value.preco),
        categoria: form.value.categoria,
        url_imagem: form.value.url_imagem || null,
        ativo: form.value.ativo
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Erro ao salvar o produto.');
    }

    modalAberto.value = false;
    buscarProdutos();
    emit('atualizar-catalogo');
  } catch (err) {
    erroForm.value = err.message;
  } finally {
    salvando.value = false;
  }
};

// Excluir Produto (Com verificação inteligente no backend)
const excluirProduto = async (produto) => {
  if (!confirm(`Deseja realmente remover ou desativar "${produto.nome}"?`)) {
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/produtos/${produto.id}`, {
      method: 'DELETE',
      headers: {
        'X-Admin-Token': ADMIN_TOKEN
      }
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Erro ao remover o produto.');
    }

    alert(data.mensagem);
    buscarProdutos();
    emit('atualizar-catalogo');
  } catch (err) {
    alert(err.message);
  }
};

// Métricas Dinâmicas
const totalProdutos = computed(() => produtos.value.length);
const ativosCount = computed(() => produtos.value.filter(p => p.ativo).length);
const inativosCount = computed(() => produtos.value.filter(p => !p.ativo).length);
</script>

<template>
  <div class="admin-container">
    
    <!-- 1. TELA DE LOGIN PRIVADO -->
    <div v-if="!autenticado" class="admin-login-card">
      <div class="login-header">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-lock">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
        <h3>Acesso Restrito</h3>
        <p>Insira a chave administrativa para gerenciar o cardápio</p>
      </div>

      <div class="form-group">
        <input 
          type="password" 
          v-model="chaveAdminInput" 
          placeholder="Digite a chave (ex: admin)" 
          @keyup.enter="realizarLogin"
          class="input-gourmet"
        />
        <p v-if="erroLogin" class="error-text">{{ erroLogin }}</p>
      </div>

      <button @click="realizarLogin" class="btn-gourmet btn-block">
        Autenticar Painel
      </button>
    </div>

    <!-- 2. PAINEL DE CONTROLE (ADMIN DASHBOARD) -->
    <div v-else class="admin-dashboard">
      
      <!-- Cabeçalho do Dashboard -->
      <div class="dashboard-header">
        <div>
          <h2>Painel de Gestão do Cardápio</h2>
          <p>Adicione novos pratos, gerencie preços e controle a disponibilidade de itens em tempo real</p>
        </div>
        <button @click="abrirNovoModal" class="btn-gourmet">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="icon-add">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Novo Produto
        </button>
      </div>

      <!-- Métricas Principais -->
      <div class="metrics-grid">
        <div class="metric-card">
          <span class="label">Total de Itens</span>
          <span class="value">{{ totalProdutos }}</span>
          <span class="subtext">Cadastrados no cardápio</span>
        </div>
        <div class="metric-card">
          <span class="label">Produtos Ativos</span>
          <span class="value success-color">{{ ativosCount }}</span>
          <span class="subtext">Visíveis para o cliente</span>
        </div>
        <div class="metric-card">
          <span class="label">Produtos Inativos</span>
          <span class="value error-color">{{ inativosCount }}</span>
          <span class="subtext">Ocultos no catálogo</span>
        </div>
        <div class="metric-card">
          <span class="label">Status da Conexão</span>
          <span class="value text-glow">Online</span>
          <span class="subtext">Supabase conectado</span>
        </div>
      </div>

      <!-- Tabela de Produtos -->
      <div class="table-container">
        <div v-if="carregando" class="loading-state">
          <div class="spinner"></div>
          <p>Carregando banco de dados...</p>
        </div>
        
        <div v-else-if="erro" class="error-state">
          <p>Ocorreu um erro: {{ erro }}</p>
          <button @click="buscarProdutos" class="btn-secondary">Tentar Novamente</button>
        </div>

        <table v-else class="admin-table">
          <thead>
            <tr>
              <th width="80">Foto</th>
              <th>Produto</th>
              <th>Categoria</th>
              <th width="120">Preço</th>
              <th width="120" class="text-center">Status</th>
              <th width="140" class="text-center">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="produto in produtos" :key="produto.id" :class="{ 'row-inactive': !produto.ativo }">
              <td>
                <img 
                  :src="produto.url_imagem || 'https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=100'" 
                  class="admin-thumb" 
                  alt="Thumb" 
                />
              </td>
              <td>
                <div class="admin-prod-info">
                  <strong>{{ produto.nome }}</strong>
                  <p>{{ produto.descricao || 'Sem descrição.' }}</p>
                </div>
              </td>
              <td>
                <span class="admin-tag">{{ produto.categoria }}</span>
              </td>
              <td>
                <strong>R$ {{ Number(produto.preco).toFixed(2).replace('.', ',') }}</strong>
              </td>
              <td class="text-center">
                <label class="toggle-switch">
                  <input 
                    type="checkbox" 
                    :checked="produto.ativo" 
                    @change="alternarAtivo(produto)" 
                  />
                  <span class="toggle-slider"></span>
                </label>
              </td>
              <td class="text-center">
                <div class="action-buttons">
                  <button @click="abrirEditarModal(produto)" class="btn-action edit" title="Editar">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                      <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4z" />
                    </svg>
                  </button>
                  <button @click="excluirProduto(produto)" class="btn-action delete" title="Excluir">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="3 6 5 6 21 6" />
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                      <line x1="10" y1="11" x2="10" y2="17" />
                      <line x1="14" y1="11" x2="14" y2="17" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>

    <!-- 3. MODAL DE CADASTRO/EDIÇÃO (POPUP) -->
    <div v-if="modalAberto" class="admin-modal-overlay">
      <div class="admin-modal">
        <div class="modal-header">
          <h3>{{ editandoId ? 'Editar Produto' : 'Cadastrar Novo Produto' }}</h3>
          <button @click="modalAberto = false" class="btn-close">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <p v-if="erroForm" class="error-banner">{{ erroForm }}</p>
          
          <div class="form-grid">
            <div class="form-group span-2">
              <label>Nome do Produto *</label>
              <input type="text" v-model="form.nome" placeholder="Ex: Pizza Quatro Queijos" class="input-gourmet" />
            </div>

            <div class="form-group">
              <label>Categoria *</label>
              <select v-model="form.categoria" class="select-gourmet">
                <option value="pizzas">Pizzas</option>
                <option value="doces">Doces</option>
                <option value="bebidas">Bebidas</option>
              </select>
            </div>

            <div class="form-group">
              <label>Preço Unitário (R$) *</label>
              <input type="number" step="0.01" v-model="form.preco" placeholder="Ex: 45.90" class="input-gourmet" />
            </div>

            <div class="form-group span-2">
              <label>Descrição do Prato</label>
              <textarea v-model="form.descricao" placeholder="Descreva os ingredientes de forma apetitosa..." rows="3" class="textarea-gourmet"></textarea>
            </div>

            <div class="form-group span-2">
              <label>URL da Imagem (Link do Unsplash/Internet)</label>
              <input type="url" v-model="form.url_imagem" placeholder="https://images.unsplash.com/..." class="input-gourmet" />
            </div>

            <div class="form-group span-2 flex-row">
              <label class="toggle-switch">
                <input type="checkbox" v-model="form.ativo" />
                <span class="toggle-slider"></span>
              </label>
              <span>Disponibilizar este produto imediatamente no catálogo</span>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="modalAberto = false" class="btn-secondary">Cancelar</button>
          <button @click="salvarProduto" class="btn-gourmet" :disabled="salvando">
            {{ salvando ? 'Salvando...' : 'Salvar Alterações' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
