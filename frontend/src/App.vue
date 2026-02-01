<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 font-sans antialiased text-slate-900">
    
    <nav class="bg-slate-900 text-white shadow-xl sticky top-0 z-50">
      <div class="w-full px-6"> <div class="flex items-center justify-between h-16">
          
          <div class="flex items-center gap-3">
            <div class="bg-blue-600 p-1.5 rounded-lg shadow-lg shadow-blue-500/30">
              <span class="text-xl">🏥</span>
            </div>
            <span class="font-extrabold text-xl tracking-tight uppercase italic">
              Empresa_X <span class="text-blue-400">Analytics</span>
            </span>
          </div>

          <div class="flex gap-2">
            <button 
              @click="currentView = 'dashboard'" 
              :class="['px-4 py-2 rounded-full text-sm font-bold transition-all duration-300', currentView === 'dashboard' ? 'bg-blue-600 shadow-lg scale-105' : 'text-slate-300 hover:bg-slate-800']"
            >Dashboard</button>
            <button 
              @click="currentView = 'list'" 
              :class="['px-4 py-2 rounded-full text-sm font-bold transition-all duration-300', (currentView === 'list' || currentView === 'detail') ? 'bg-blue-600 shadow-lg scale-105' : 'text-slate-300 hover:bg-slate-800']"
            >Operadoras</button>
          </div>
        </div>
      </div>
    </nav>

    <main class="w-full px-6 py-8 animate-fade-in"> <section v-if="currentView === 'dashboard'">
        <Dashboard />
      </section>

      <section v-else-if="currentView === 'list'">
        <OperadorasTable @select="verDetalhes" />
      </section>

      <section v-else-if="currentView === 'detail'">
        <OperadoraDetail :cnpj="selectedCnpj" @back="currentView = 'list'" />
      </section>

    </main>
    
    <footer class="text-center py-8 text-slate-400 text-sm font-medium">
      © 2026 EMPRESA_X - Talita Mendonça Marques
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Dashboard from './components/Dashboard.vue'
import OperadorasTable from './components/OperadorasTable.vue'
import OperadoraDetail from './components/OperadoraDetail.vue'

const currentView = ref('dashboard')
const selectedCnpj = ref(null)

const verDetalhes = (cnpj) => {
  selectedCnpj.value = cnpj
  currentView.value = 'detail'
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.5s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>