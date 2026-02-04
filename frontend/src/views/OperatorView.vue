<template>
  <div class="details-page">
    <div class="container">
      <button @click="goBack" class="back-btn">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="20" 
          height="20" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2" 
          stroke-linecap="round" 
          stroke-linejoin="round"
        >
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        Voltar para a lista
      </button>

      <div v-if="loading" class="state-container loading-state">
        <div class="spinner"></div>
        <p>Carregando dados da operadora...</p>
      </div>

      <div v-else-if="error" class="state-container error-state">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="48" 
          height="48" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="#DC2626" 
          stroke-width="2" 
          stroke-linecap="round" 
          stroke-linejoin="round"
        >
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
          <line x1="12" y1="9" x2="12" y2="13"></line>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
        <h3>Serviço Indisponível</h3>
        <p>Não foi possível conectar ao servidor. Verifique se o backend está rodando.</p>
        <button @click="loadData" class="retry-btn">
          Tentar Novamente
        </button>
      </div>

      <div v-else-if="operator" class="content-wrapper">
        
        <div class="info-card">
          <h1>{{ operator.razao_social }}</h1>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">CNPJ</span>
              <span class="value">{{ operator.cnpj }}</span>
            </div>
            <div class="info-item">
              <span class="label">Registro ANS</span>
              <span class="value">{{ operator.registro_ans }}</span>
            </div>
            <div class="info-item">
              <span class="label">UF</span>
              <span class="value">{{ operator.uf }}</span>
            </div>
            <div class="info-item">
              <span class="label">Modalidade</span>
              <span class="value">{{ operator.modalidade }}</span>
            </div>
          </div>
        </div>

        <div class="history-section">
          <h2>Histórico de Despesas</h2>
          
          <table class="history-table">
            <thead>
              <tr>
                <th class="col-ano text-left">Ano</th>
                <th class="col-tri text-center">Trimestre</th>
                <th class="col-valor text-right">Valor da Despesa</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="expense in expenses" :key="expense.id">
                <td class="col-ano text-left">{{ expense.ano }}</td>
                <td class="col-tri text-center">{{ expense.trimestre }}º Trimestre</td>
                <td class="col-valor text-right valor">
                  {{ formatCurrency(expense.valor_despesa) }}
                </td>
              </tr>
              <tr v-if="expenses.length === 0">
                <td colspan="3" class="empty-state">Sem despesas registradas.</td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../services/api';

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const error = ref(false);
const operator = ref(null);
const expenses = ref([]);

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
};

const goBack = () => {
  router.push('/');
};

const loadData = async () => {
  loading.value = true;
  error.value = false;
  const cnpj = route.params.cnpj;

  try {
    const [opResponse, expResponse] = await Promise.all([
      api.get(`/operadoras/${cnpj}`),
      api.get(`/operadoras/${cnpj}/despesas`)
    ]);

    operator.value = opResponse.data;
    expenses.value = expResponse.data;
  } catch (err) {
    console.error("Erro ao carregar detalhes", err);
    error.value = true;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.details-page {
  min-height: 100vh;
  background-color: #F9FAFB;
  padding: 40px 0;
  font-family: 'Inter', sans-serif;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.back-btn {
  background: none;
  border: none;
  color: #2563EB;
  font-weight: 500;
  cursor: pointer;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0;
  font-size: 14px;
}
.back-btn:hover { text-decoration: underline; }

.state-container {
  background: white;
  border: 1.5px solid #E5E7EB;
  border-radius: 8px;
  padding: 60px 20px;
  text-align: center;
  margin-top: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-state { color: #6B7280; gap: 20px; }

.spinner {
  width: 40px; height: 40px;
  border: 4px solid #E5E7EB; border-top: 4px solid #2563EB;
  border-radius: 50%; animation: spin 1s linear infinite;
}

.error-state svg { margin-bottom: 20px; color: #DC2626; }
.error-state h3 { font-size: 20px; color: #1F2937; margin-bottom: 10px; font-weight: 700; }
.error-state p { color: #6B7280; font-size: 15px; margin-bottom: 25px; }

.retry-btn {
  background-color: #DC2626; color: white; border: none;
  padding: 10px 24px; border-radius: 6px; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: background 0.2s;
}
.retry-btn:hover { background-color: #B91C1C; }

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.info-card {
  background: white;
  border: 1.5px solid #E5E7EB;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 24px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.info-card h1 {
  font-size: 20px;
  color: #111827;
  margin-bottom: 24px;
  padding-bottom: 15px;
  border-bottom: 1px solid #E5E7EB;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.info-item { display: flex; flex-direction: column; }
.label { font-size: 12px; color: #6B7280; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }
.value { font-size: 15px; color: #1F2937; font-weight: 500; }

.history-section {
  background: white;
  border: 1.5px solid #E5E7EB;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.history-section h2 {
  font-size: 16px;
  color: #374151;
  margin-bottom: 20px;
  font-weight: 600;
}

.history-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
.history-table th { padding: 12px; font-size: 13px; color: #6B7280; border-bottom: 2px solid #E5E7EB; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.history-table td { padding: 16px 12px; font-size: 14px; color: #374151; border-bottom: 1px solid #F3F4F6; }

.col-ano, .col-tri, .col-valor { width: 33.33%; }
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

.valor { color: #059669; }
.empty-state { text-align: center; color: #9CA3AF; padding: 20px; font-style: italic; }
</style>
