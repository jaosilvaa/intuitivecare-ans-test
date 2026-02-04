<template>
  <div class="table-container">
    <div class="section-header">
      <h2>Lista de Operadoras</h2>
      <span class="results-info" v-if="operators.length > 0">
        Total: {{ total }} registros
      </span>
    </div>

    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Razão Social</th>
            <th>CNPJ</th>
            <th>UF</th>
            <th class="text-right">Modalidade</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="op in operators" 
            :key="op.registro_ans" 
            @click="$emit('select', op.cnpj)"
            class="clickable-row"
          >
            <td class="main-col">{{ op.razao_social }}</td>
            <td>{{ op.cnpj }}</td>
            <td>
              <span class="uf-badge">{{ op.uf }}</span>
            </td>
            <td class="text-right">{{ op.modalidade }}</td>
          </tr>

          <tr v-if="operators.length === 0">
            <td colspan="4" class="empty-state">
              Nenhuma operadora encontrada.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button 
        :disabled="page === 1" 
        @click="$emit('change-page', page - 1)"
        class="nav-text-btn"
      >
        Anterior
      </button>
      
      <div class="page-numbers">
        <button 
          v-for="p in visiblePages" 
          :key="p"
          class="page-box"
          :class="{ active: p === page }"
          @click="$emit('change-page', p)"
        >
          {{ p }}
        </button>
      </div>

      <button 
        :disabled="page >= totalPages" 
        @click="$emit('change-page', page + 1)"
        class="nav-text-btn"
      >
        Próxima
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  operators: Array,
  page: Number,
  limit: Number,
  total: Number
});

defineEmits(['change-page', 'select']);

const totalPages = computed(() => Math.ceil(props.total / props.limit));

const visiblePages = computed(() => {
  const pages = [];
  const maxVisible = 5;
  
  let start = props.page - 2;
  let end = props.page + 2;

  if (start < 1) {
    start = 1;
    end = Math.min(maxVisible, totalPages.value);
  }

  if (end > totalPages.value) {
    end = totalPages.value;
    start = Math.max(1, end - maxVisible + 1);
  }

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  
  return pages;
});
</script>

<style scoped>
.table-container {
  background: white;
  border: 1.5px solid #E5E7EB;
  border-radius: 8px;
  padding: 24px;
  margin-top: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 16px;
  color: #1F2937;
  font-weight: 600;
}

.results-info {
  font-size: 13px;
  color: #6B7280;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  padding: 12px;
  font-size: 12px;
  color: #6B7280;
  font-weight: 700;
  border-bottom: 2px solid #E5E7EB;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: 16px 12px;
  font-size: 14px;
  color: #374151;
  border-bottom: 1px solid #F3F4F6;
  transition: all 0.2s;
}

.clickable-row {
  cursor: pointer;
}

.clickable-row:hover td {
  background-color: #EFF6FF;
  color: #1D4ED8;
}

.main-col {
  font-weight: 500;
  color: #111827;
}

.text-right { text-align: right; }

.uf-badge {
  background-color: #F3F4F6;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #9CA3AF;
  font-style: italic;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
  gap: 15px;
  padding-top: 20px;
  border-top: 1px solid #E5E7EB;
}

.nav-text-btn {
  background: none;
  border: none;
  color: #4B5563;
  font-size: 14px;
  font-weight: 400;
  cursor: pointer;
  padding: 5px 10px;
}

.nav-text-btn:hover:not(:disabled) {
  color: #2563EB;
}

.nav-text-btn:disabled {
  color: #D1D5DB;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 5px;
}

.page-box {
  background: transparent;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 400;
  color: #4B5563;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.page-box:hover:not(.active) {
  background-color: #F3F4F6;
  color: #2563EB;
}

.page-box.active {
  background-color: #2563EB;
  color: white;
  font-weight: 500;
}
</style>
