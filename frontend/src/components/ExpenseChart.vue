<template>
  <div class="chart-container">
    <div class="section-header">
      <h2>Distribuição de Despesas por UF</h2>
    </div>
    
    <div class="canvas-wrapper">
      <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
      <p v-else class="loading-text">Aguardando dados...</p>
    </div>
  </div>
</template>

<script setup>
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

defineProps({
  chartData: {
    type: Object,
    default: null
  }
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }, 
    tooltip: { 
      backgroundColor: '#1F2937',
      titleColor: '#fff',
      bodyColor: '#fff',
      callbacks: {
        label: (context) => {
          return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(context.raw);
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: '#f3f4f6' },
      ticks: { 
        color: '#6b7280',
        callback: (value) => {
          if (value >= 1000000000) {
            return (value / 1000000000).toFixed(1).replace('.', ',') + ' Bi';
          }
          if (value >= 1000000) {
            return (value / 1000000).toFixed(1).replace('.', ',') + ' Mi';
          }
          return value;
        }
      }
    },
    x: {
      grid: { display: false },
      ticks: { color: '#1f2937' }
    }
  }
};
</script>

<style scoped>
.chart-container {
  background: white;
  border: 1.5px solid #E5E7EB;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.section-header h2 {
  font-size: 16px;
  color: #1F2937;
  margin-bottom: 20px;
  font-weight: 600;
}

.canvas-wrapper {
  height: 300px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-text {
  color: #6B7280;
  text-align: center;
  font-size: 14px;
}
</style>
