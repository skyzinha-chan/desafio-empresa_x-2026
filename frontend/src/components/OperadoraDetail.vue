<template>
  <div class="w-full space-y-6">
    <button
      @click="$emit('back')"
      class="group flex items-center gap-2 text-slate-500 hover:text-blue-600 font-medium transition-colors w-fit"
    >
      <div
        class="p-1.5 rounded-full bg-slate-100 group-hover:bg-blue-100 transition-colors"
      >
        <svg
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10 19l-7-7m0 0l7-7m-7 7h18"
          ></path>
        </svg>
      </div>
      Voltar para a lista
    </button>

    <div
      v-if="loading"
      class="w-full bg-white rounded-2xl shadow-xl border border-slate-100 p-8 animate-pulse"
    >
      <div class="h-8 bg-slate-200 rounded w-1/3 mb-6"></div>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="h-12 bg-slate-100 rounded"></div>
        <div class="h-12 bg-slate-100 rounded"></div>
        <div class="h-12 bg-slate-100 rounded"></div>
        <div class="h-12 bg-slate-100 rounded"></div>
      </div>
      <div class="h-64 bg-slate-50 rounded"></div>
    </div>

    <div v-else-if="data" class="w-full space-y-6">
      <div
        class="w-full bg-white rounded-2xl shadow-xl border border-slate-100 p-6 md:p-8"
      >
        <div class="flex flex-col md:flex-row gap-6 items-start">
          <div
            class="shrink-0 p-4 bg-blue-50 rounded-2xl border border-blue-100 shadow-sm flex items-center justify-center"
          >
            <svg
              class="w-12 h-12 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
              />
            </svg>
          </div>

          <div class="flex-1 w-full">
            <div
              class="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-6"
            >
              <h2
                class="text-2xl md:text-3xl font-extrabold text-slate-800 tracking-tight uppercase break-words leading-tight"
              >
                {{ data.operadora.razao_social }}
              </h2>
              <span
                class="shrink-0 inline-flex items-center px-4 py-1.5 rounded-full text-sm font-bold bg-emerald-100 text-emerald-800 border border-emerald-200 shadow-sm"
              >
                Operadora Ativa
              </span>
            </div>

            <div
              class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full"
            >
              <div
                class="bg-slate-50 p-3.5 rounded-xl border border-slate-100 hover:border-blue-200 transition-colors"
              >
                <p
                  class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1"
                >
                  CNPJ
                </p>
                <p class="font-mono text-slate-800 font-bold">
                  {{ formatCnpj(data.operadora.cnpj) }}
                </p>
              </div>
              <div
                class="bg-slate-50 p-3.5 rounded-xl border border-slate-100 hover:border-blue-200 transition-colors"
              >
                <p
                  class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1"
                >
                  Registro ANS
                </p>
                <p class="font-mono text-slate-800 font-bold">
                  {{ data.operadora.registro_ans }}
                </p>
              </div>
              <div
                class="bg-slate-50 p-3.5 rounded-xl border border-slate-100 hover:border-blue-200 transition-colors"
              >
                <p
                  class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1"
                >
                  UF Sede
                </p>
                <p class="text-slate-800 font-bold">{{ data.operadora.uf }}</p>
              </div>
              <div
                class="bg-slate-50 p-3.5 rounded-xl border border-slate-100 hover:border-blue-200 transition-colors"
              >
                <p
                  class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1"
                >
                  Modalidade
                </p>
                <p
                  class="text-slate-800 font-bold truncate"
                  :title="data.operadora.modalidade"
                >
                  {{ data.operadora.modalidade }}
                </p>
              </div>
              

              <div
                class="bg-slate-50 p-3.5 rounded-xl border border-slate-100 hover:border-blue-200 transition-colors"
              >
                <p
                  class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1"
                >
                  Cidade
                </p>
                <p class="text-slate-800 font-bold truncate">
                  {{ data.operadora.cidade || "N/I" }}
                </p>
              </div>

              <div
                class="bg-slate-50 p-3.5 rounded-xl border border-slate-100 hover:border-blue-200 transition-colors"
              >
                <p
                  class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1"
                >
                  Contato
                </p>
                <div class="flex flex-col">
                  <span
                    class="text-xs text-slate-600 truncate"
                    v-if="data.operadora.telefone"
                    >📞 {{ data.operadora.telefone }}</span
                  >
                  <span
                    class="text-xs text-slate-600 truncate"
                    v-if="data.operadora.email"
                    >✉️ {{ data.operadora.email }}</span
                  >
                  <span
                    class="text-slate-400 text-xs"
                    v-if="!data.operadora.telefone && !data.operadora.email"
                    >Não informado</span
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

<div v-if="data.despesas.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
  <div class="bg-white p-5 rounded-2xl shadow-lg border border-slate-100 flex items-center justify-between">
    <div>
      <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Acumulado (Ano)</p>
      <p class="text-2xl font-extrabold text-slate-800 mt-1">{{ formatCurrency(kpis.total) }}</p>
    </div>
    <div class="p-3 bg-blue-50 text-blue-600 rounded-xl">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
    </div>
  </div>

  <div class="bg-white p-5 rounded-2xl shadow-lg border border-slate-100 flex items-center justify-between">
    <div>
      <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Média Trimestral</p>
      <p class="text-2xl font-extrabold text-slate-800 mt-1">{{ formatCurrency(kpis.media) }}</p>
    </div>
    <div class="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
    </div>
  </div>

</div>


      <div
        class="w-full bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden"
      >
      
<div class="p-6 border-b border-slate-100 bg-white">
          <h3 class="text-xl font-bold text-slate-800 flex items-center gap-3">
            Histórico Financeiro
            <span
              class="text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1 rounded-full border border-slate-200"
            >
              Despesas com Eventos (411)
            </span>
          </h3>
        </div>

        <div v-if="data.despesas.length > 0" class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead class="bg-slate-50/80">
              <tr>
                <th
                  class="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider"
                >
                  Ano
                </th>
                <th
                  class="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider"
                >
                  Período
                </th>
                <th
                  class="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right"
                >
                  Valor Reportado
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="(item, index) in data.despesas"
                :key="index"
                class="hover:bg-blue-50/30 transition-colors"
              >
                <td class="px-6 py-4 font-bold text-slate-700">
                  {{ item.ano }}
                </td>
                <td class="px-6 py-4 text-slate-600">
                  <span class="inline-flex items-center gap-2">
                    <span
                      class="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-sm shadow-blue-500/50"
                    ></span>
                    {{ item.trimestre }}º Trimestre
                  </span>
                </td>
                <td class="px-6 py-4 text-right">
                  <span class="font-mono font-bold text-slate-800 text-lg">
                    {{ formatCurrency(item.valor_despesa) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-else
          class="flex flex-col items-center justify-center py-16 px-4 bg-slate-50/50"
        >
          <div class="bg-white p-4 rounded-full shadow-sm mb-4">
            <span class="text-4xl filter grayscale opacity-70">📄</span>
          </div>
          <h4 class="text-lg font-bold text-slate-700 mb-2">
            Sem histórico financeiro recente
          </h4>
          <p
            class="text-slate-500 text-center max-w-md text-sm leading-relaxed"
          >
            Esta operadora não reportou despesas com eventos/sinistros (conta
            contábil 411) nos arquivos oficiais da ANS processados pelo sistema.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { operadoraService } from "../services/api";

const props = defineProps(["cnpj"]);
const data = ref(null);
const loading = ref(true);

const formatCurrency = (val) => {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(val);
};

// Função de Máscara de CNPJ
const formatCnpj = (v) => {
  if (!v) return "";
  // Converte para string e remove o que não for número
  const value = String(v).replace(/\D/g, "");
  // Aplica a formatação XX.XXX.XXX/YYYY-ZZ
  return value.replace(
    /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
    "$1.$2.$3/$4-$5",
  );
};

const kpis = computed(() => {
  if (!data.value?.despesas || data.value.despesas.length === 0) {
    return { total: 0, media: 0 };
  }
  const total = data.value.despesas.reduce(
    (acc, curr) => acc + Number(curr.valor_despesa),
    0,
  );
  const media = total / data.value.despesas.length;
  return { total, media };
});

onMounted(async () => {
  try {
    const response = await operadoraService.detalhes(props.cnpj);
    data.value = response.data;
  } catch (error) {
    console.error("Erro ao carregar detalhes:", error);
  } finally {
    loading.value = false;
  }
});
</script>
