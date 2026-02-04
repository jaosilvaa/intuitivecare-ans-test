<template>
  <div class="dashboard">
    <header class="top-bar">
      <div class="container">
        <h1>Intuitive Care | Operadoras ANS</h1>
      </div>
    </header>

    <main class="container content">
      
      <div v-if="globalError" class="state-container error-state">
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
        <button @click="initialLoad" class="retry-btn">
          Tentar Novamente
        </button>
      </div>

      <div v-else-if="initialLoading" class="state-container loading-state">
        <div class="spinner"></div>
        <p>Carregando dashboard...</p>
      </div>

      <div v-else>
        <section class="search-section">
          <label for="search">Buscar Operadora</label>
          <div class="input-wrapper">
            <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input 
              id="search"
              type="text" 
              v-model="searchQuery" 
              @keydown.enter="triggerSearch"
              placeholder="Digite a razão social ou CNPJ"
            />
          </div>
        </section>

        <section class="chart-section">
          <ExpenseChart :chartData="chartData" />
        </section>

        <section class="table-section">
          <OperatorTable 
            :operators="operators" 
            :page="page" 
            :limit="limit"
            :total="totalItems"
            @change-page="changePage"
            @select="goToDetails"
          />
        </section>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';
import ExpenseChart from '../components/ExpenseChart.vue';
import OperatorTable from '../components/OperatorTable.vue';

const router = useRouter();

const operators = ref([]);
const chartData = ref(null);
const totalItems = ref(0);

const searchQuery = ref('');
const page = ref(1);
const limit = 10;
const initialLoading = ref(true);
const globalError = ref(false);

const initialLoad = async () => {
  initialLoading.value = true;
  globalError.value = false;

  try {
    const params = { page: 1, limit: limit };
    
    const [chartResponse, tableResponse] = await Promise.all([
      api.get('/estatisticas'),
      api.get('/operadoras', { params })
    ]);

    const ufData = chartResponse.data.por_uf;
    chartData.value = {
      labels: ufData.map(item => item.uf),
      datasets: [{
        label: 'Total por UF',
        backgroundColor: '#2563EB', 
        borderRadius: 4,
        maxBarThickness: 75,
        data: ufData.map(item => item.total)
      }]
    };

    operators.value = tableResponse.data.data;
    totalItems.value = tableResponse.data.total;

  } catch (error) {
    console.error("Erro crítico ao carregar dashboard", error);
    globalError.value = true;
  } finally {
    initialLoading.value = false;
  }
};

const fetchOperatorsOnly = async () => {
  try {
    const params = {
      page: page.value,
      limit: limit,
      search: searchQuery.value
    };
    const response = await api.get('/operadoras', { params });
    operators.value = response.data.data;
    totalItems.value = response.data.total;
  } catch (error) {
    console.error("Erro na busca", error);
    alert("Erro ao buscar dados. Verifique sua conexão.");
  }
};

const triggerSearch = () => {
  page.value = 1;
  fetchOperatorsOnly();
};

const changePage = (newPage) => {
  page.value = newPage;
  fetchOperatorsOnly();
};

const goToDetails = (cnpj) => {
  router.push(`/operadora/${cnpj}`);
};

onMounted(() => {
  initialLoad();
});
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #FFFFFF;
  font-family: 'Inter', sans-serif;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

.top-bar {
  border-bottom: 1.5px solid #E5E7EB;
  padding: 20px 0;
  margin-bottom: 30px;
}

.top-bar h1 {
  font-size: 24px;
  color: #1F2937;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.search-section { margin-bottom: 30px; }
.search-section label { display: block; font-size: 14px; color: #374151; margin-bottom: 8px; font-weight: 500; }
.input-wrapper { position: relative; }
.search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: #9CA3AF; pointer-events: none; }

input {
  width: 100%; box-sizing: border-box; display: block; margin: 0;
  padding: 12px 12px 12px 45px; border: 1.5px solid #E5E7EB; border-radius: 8px;
  font-size: 15px; color: #1F2937; outline: none; transition: border-color 0.2s; font-family: inherit;
}
input:focus { border-color: #2563EB; }
input::placeholder { color: #9CA3AF; }

.chart-section { margin-bottom: 24px; }

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
</style>
