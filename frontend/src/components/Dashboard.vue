<template>
  <div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      
      <div class="bg-white p-6 rounded-2xl shadow-lg border border-slate-100 flex items-start justify-between hover:shadow-xl transition-shadow duration-300">
        <div>
          <p class="text-sm font-bold text-slate-400 uppercase tracking-wider">Total Geral</p>
          <h3 class="text-2xl font-extrabold text-slate-800 mt-2">
            <span v-if="loading" class="animate-pulse bg-slate-200 h-8 w-32 block rounded"></span>
            <span v-else>{{ formatCurrency(stats.kpis.total_despesas) }}</span>
          </h3>
        </div>
        <div class="p-3 bg-blue-50 text-blue-600 rounded-xl">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        </div>
      </div>

      <div class="bg-white p-6 rounded-2xl shadow-lg border border-slate-100 flex items-start justify-between hover:shadow-xl transition-shadow duration-300">
        <div>
          <p class="text-sm font-bold text-slate-400 uppercase tracking-wider">Média / Lançamento</p>
          <h3 class="text-2xl font-extrabold text-slate-800 mt-2">
            <span v-if="loading" class="animate-pulse bg-slate-200 h-8 w-24 block rounded"></span>
            <span v-else>{{ formatCurrency(stats.kpis.media_por_lancamento) }}</span>
          </h3>
        </div>
        <div class="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
        </div>
      </div>

      <div class="bg-white p-6 rounded-2xl shadow-lg border border-slate-100 flex items-start justify-between hover:shadow-xl transition-shadow duration-300">
        <div>
          <p class="text-sm font-bold text-slate-400 uppercase tracking-wider">Top Operadoras</p>
          <h3 class="text-2xl font-extrabold text-slate-800 mt-2">
            <span v-if="loading" class="animate-pulse bg-slate-200 h-8 w-16 block rounded"></span>
            <span v-else>{{ stats.top_operadoras.length }} <span class="text-sm font-medium text-slate-400">no ranking</span></span>
          </h3>
        </div>
        <div class="p-3 bg-amber-50 text-amber-600 rounded-xl">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      
      <div class="bg-white p-6 rounded-2xl shadow-lg border border-slate-100 flex flex-col">
        <h3 class="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
          <span class="w-2 h-6 bg-blue-600 rounded-full"></span>
          Distribuição por UF
        </h3>
        <div class="h-80 relative w-full">
          <div v-if="loading" class="h-full flex items-center justify-center">
             <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
          <Bar v-else-if="chartData.labels.length > 0" :data="chartData" :options="chartOptions" />
          <div v-else class="h-full flex items-center justify-center text-slate-400">
            Sem dados para exibir.
          </div>
        </div>
      </div>

      <div class="bg-white p-6 rounded-2xl shadow-lg border border-slate-100">
        <h3 class="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
          <span class="w-2 h-6 bg-amber-500 rounded-full"></span>
          Maiores Despesas (Top 5)
        </h3>
        
        <div v-if="loading" class="space-y-4">
           <div v-for="i in 5" :key="i" class="h-16 bg-slate-50 rounded-lg animate-pulse"></div>
        </div>

        <ul v-else class="space-y-3">
          <li v-for="(op, index) in stats.top_operadoras" :key="op.razao_social" 
              class="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100 group">
            
            <div class="flex items-center gap-4">
              <div class="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-slate-100 text-slate-600 font-bold rounded-full group-hover:bg-blue-100 group-hover:text-blue-700 transition-colors">
                {{ index + 1 }}
              </div>
              
              <div>
                <p class="font-bold text-slate-700 text-sm md:text-base line-clamp-1">{{ op.razao_social }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <span class="px-2 py-0.5 bg-slate-100 text-slate-500 text-xs rounded-md font-medium">{{ op.uf }}</span>
                  <span class="text-xs text-slate-400 hidden sm:inline">• Registro Ativo</span>
                </div>
              </div>
            </div>

            <div class="text-right">
              <span class="block font-bold text-slate-800 group-hover:text-blue-700 transition-colors">
                {{ formatCurrency(op.total) }}
              </span>
            </div>
          </li>
        </ul>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { operadoraService } from '../services/api'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

// Registro do ChartJS
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

// Estados Reativos
const loading = ref(true)
const stats = reactive({
  kpis: { total_despesas: 0, media_por_lancamento: 0 },
  top_operadoras: [],
  distribuicao_uf: []
})
const chartData = ref({ labels: [], datasets: [] })

// Configurações do Gráfico (Refinadas)
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: (context) => {
          let label = context.dataset.label || '';
          if (label) label += ': ';
          if (context.parsed.y !== null) {
            label += new Intl.NumberFormat('pt-BR', { 
              style: 'currency', currency: 'BRL' 
            }).format(context.parsed.y);
          }
          return label;
        }
      }
    }
  },
  scales: {
    x: {
      grid: { display: false } // Remove grade vertical para limpar o visual
    },
    y: {
      beginAtZero: true,
      border: { display: false }, // Remove borda do eixo Y
      grid: {
        color: '#f1f5f9', // Linhas de grade muito sutis
        borderDash: [5, 5] // Linhas pontilhadas
      },
      ticks: {
        font: { size: 11 },
        color: '#64748b',
        callback: (value) => {
          if (value >= 1e9) return (value / 1e9).toFixed(1) + 'B';
          if (value >= 1e6) return (value / 1e6).toFixed(1) + 'M';
          if (value >= 1e3) return (value / 1e3).toFixed(0) + 'K';
          return value;
        }
      }
    }
  }
}

// Helpers
const formatCurrency = (val) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val)
}

// Lógica de Carregamento
const loadDashboard = async () => {
  loading.value = true
  try {
    const { data } = await operadoraService.estatisticas()
    Object.assign(stats, data)

    // Configuração visual do gráfico
    chartData.value = {
      labels: data.distribuicao_uf.map(item => item.uf),
      datasets: [{
        label: 'Total por UF',
        backgroundColor: '#3b82f6', // blue-500
        hoverBackgroundColor: '#1d4ed8', // blue-700
        borderRadius: 4, // Barras levemente arredondadas
        barPercentage: 0.6, // Barras mais finas e elegantes
        data: data.distribuicao_uf.map(item => item.total)
      }]
    }
  } catch (error) {
    console.error("Erro ao carregar dashboard:", error)
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>