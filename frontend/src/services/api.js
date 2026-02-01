// frontend/src/services/api.js
import axios from 'axios'

const api = axios.create( {
    // URL onde seu FastAPI está rodando (conforme vimos no terminal anteriormente)
    baseURL: 'http://localhost:8000/api',
} )

export const operadoraService = {
    // Rota que você validou no Swagger: /api/operadoras
    listar: ( page = 1, search = '', filter_type = 'todas', sort_uf = null ) => {
        // Monta a URL base
        let url = `/operadoras?page=${ page }&limit=10`

        // Adiciona parâmetros opcionais apenas se tiverem valor
        if ( search ) url += `&search=${ search }`
        if ( filter_type ) url += `&filter_type=${ filter_type }`
        if ( sort_uf ) url += `&sort_uf=${ sort_uf }`

        return api.get( url )
    },

    // Rota de detalhes enriquecidos
    detalhes: ( cnpj ) =>
        api.get( `/operadoras/${ cnpj }/despesas` ),

    // Rota das estatísticas do Dashboard (Top 5 e UFs)
    estatisticas: () =>
        api.get( '/estatisticas' ),
}