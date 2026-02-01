<template>
  <div class="bg-white rounded-xl shadow-xl border border-slate-100 overflow-hidden">
    
    <div class="p-6 pb-0 space-y-6">
      
      <div class="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h2 class="text-2xl font-bold text-slate-800">Operadoras de Saúde</h2>
          <p class="text-slate-500 mt-1">Gerencie e filtre a base cadastral</p>
        </div>
        
        <div class="relative w-full md:w-96">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          </div>
          <input 
            v-model="searchTerm"
            @input="handleSearch"
            type="text" 
            placeholder="Buscar CNPJ ou Razão Social..." 
            class="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-full text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          />
        </div>
      </div>

      <div class="flex flex-col md:flex-row justify-between items-end border-b border-slate-100 gap-4">
        
        <div class="flex gap-4 -mb-px overflow-x-auto w-full md:w-auto no-scrollbar">
          <button 
            @click="changeTab('todas')"
            :class="['pb-3 px-2 text-sm font-bold border-b-2 whitespace-nowrap transition-colors', activeTab === 'todas' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700']"
          >
            Todas
          </button>
          <button 
            @click="changeTab('com_dados')"
            :class="['pb-3 px-2 text-sm font-bold border-b-2 whitespace-nowrap transition-colors', activeTab === 'com_dados' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700']"
          >
            Com Registros
          </button>
          <button 
            @click="changeTab('sem_dados')"
            :class="['pb-3 px-2 text-sm font-bold border-b-2 whitespace-nowrap transition-colors', activeTab === 'sem_dados' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700']"
          >
            Sem Registros
          </button>
        </div>

        <div class="flex items-center gap-3 pb-2 w-full md:w-auto justify-end">
          <span class="text-xs font-medium text-slate-500">
            {{ meta.page }} / {{ meta.total_pages }}
          </span>
          <div class="flex gap-1">
            <button 
              @click="changePage(-1)" 
              :disabled="meta.page === 1" 
              class="p-1.5 rounded-md border border-slate-200 text-slate-500 hover:bg-slate-50 hover:text-blue-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Página Anterior"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
            </button>
            <button 
              @click="changePage(1)" 
              :disabled="meta.page === meta.total_pages" 
              class="p-1.5 rounded-md border border-slate-200 text-slate-500 hover:bg-slate-50 hover:text-blue-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Próxima Página"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead class="bg-slate-50/50">
          <tr>
            <th class="px-6 py-4 text-xs font-bold text-slate-500 uppercase">CNPJ</th>
            <th class="px-6 py-4 text-xs font-bold text-slate-500 uppercase w-1/2">Razão Social</th>
            
            <th 
              @click="toggleSort"
              class="px-6 py-4 text-xs font-bold text-slate-500 uppercase cursor-pointer hover:bg-slate-100 transition-colors select-none group"
            >
              <div class="flex items-center gap-1">
                UF
                <span v-if="sortOrder === 'asc'" class="text-blue-600 font-bold">↑</span>
                <span v-else-if="sortOrder === 'desc'" class="text-blue-600 font-bold">↓</span>
                <span v-else class="text-slate-300 group-hover:text-slate-500">↕</span>
              </div>
            </th>
            
            <th class="px-6 py-4 text-xs font-bold text-slate-500 uppercase text-right">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="loading"><td colspan="4" class="p-12 text-center text-slate-500 animate-pulse">Carregando dados...</td></tr>
          <tr v-else-if="operadoras.length === 0"><td colspan="4" class="p-12 text-center text-slate-500">Nenhum registro encontrado.</td></tr>
          
          <tr v-for="op in operadoras" :key="op.cnpj" class="group hover:bg-blue-50/30 transition-colors">
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="font-mono text-sm text-slate-600 bg-slate-100 px-2 py-1 rounded">{{ formatCnpj(op.cnpj) }}</span>
            </td>
            <td class="px-6 py-4">
              <div class="text-sm font-bold text-slate-700 group-hover:text-blue-700 transition-colors">
                {{ op.razao_social }}
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800 shadow-sm">
                {{ op.uf }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button @click="$emit('select', op.cnpj)" class="text-blue-600 hover:text-blue-900 font-bold hover:underline">Ver Detalhes</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
      <span class="text-sm text-slate-500 font-medium">Página {{ meta.page }} de {{ meta.total_pages }}</span>
      <div class="flex gap-2">
        <button @click="changePage(-1)" :disabled="meta.page === 1" class="px-4 py-2 text-sm font-medium bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-50 shadow-sm">Anterior</button>
        <button @click="changePage(1)" :disabled="meta.page === meta.total_pages" class="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 shadow-md shadow-blue-500/20">Próxima</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { operadoraService } from '../services/api'

const operadoras = ref([])
const searchTerm = ref('')
const loading = ref(false)
const meta = ref({ page: 1, total_pages: 1 })
const activeTab = ref('todas')
const sortOrder = ref(null)
let debounceTimer = null 

// Função de Máscara de CNPJ
const formatCnpj = (v) => {
  if (!v) return ''
  // Converte para string e remove o que não for número
  const value = String(v).replace(/\D/g, '')
  // Aplica a formatação XX.XXX.XXX/YYYY-ZZ
  return value.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5")
}

const fetchOperadoras = async () => {
  loading.value = true
  try {
    const { data } = await operadoraService.listar(
      meta.value.page, 
      searchTerm.value,
      activeTab.value,
      sortOrder.value
    )
    operadoras.value = data.data || [] 
    meta.value = data.meta || { page: 1, total_pages: 1 }
  } catch (error) {
    console.error('Erro:', error)
    operadoras.value = []
  } finally {
    loading.value = false
  }
}

const changeTab = (tab) => {
  activeTab.value = tab
  meta.value.page = 1
  fetchOperadoras()
}

const toggleSort = () => {
  if (sortOrder.value === null) sortOrder.value = 'asc'
  else if (sortOrder.value === 'asc') sortOrder.value = 'desc'
  else sortOrder.value = null
  fetchOperadoras()
}

const handleSearch = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    meta.value.page = 1
    fetchOperadoras()
  }, 400)
}

const changePage = (step) => {
  meta.value.page += step
  fetchOperadoras()
  // Scroll suave apenas se a paginação for acionada (opcional, já que agora tem botões em cima)
  // window.scrollTo({ top: 0, behavior: 'smooth' }) 
}

onMounted(fetchOperadoras)
</script>