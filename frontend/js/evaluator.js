const API_URL = "http://localhost:8000/api/opportunities";
let currentOpportunityId = null;

// Seach opportunities by ID
document.getElementById('formSearch').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const searchId = document.getElementById('searchId').value;
    const btn = document.getElementById('btnSearch');
    const errorMsg = document.getElementById('searchError');
    const panel = document.getElementById('evaluatorPanel');
    

    btn.disabled = true;
    btn.textContent = 'A procurar...';
    errorMsg.classList.add('hidden');
    panel.classList.add('hidden');
    document.getElementById('actionFeedback').classList.add('hidden');

    try {
        const response = await fetch(`${API_URL}/${searchId}`);
        const data = await response.json();

        if (response.ok) {
            currentOpportunityId = data.id;
            
            // fill the panel with the data
            document.getElementById('evalName').textContent = data.name;
            document.getElementById('evalContact').textContent = `${data.email} | ${data.phone}`;
            document.getElementById('evalScore').textContent = data.score || "A analisar";
            
            // adjust the veredict color depending the result
            const verdictEl = document.getElementById('evalVerdict');
            verdictEl.textContent = data.verdict || "Aguardando";
            verdictEl.className = "text-2xl font-bold mt-1 " + 
                (data.verdict === 'AVANÇAR' ? 'text-green-600' : 
                (data.verdict === 'PASSAR' ? 'text-red-600' : 'text-amber-500'));

            document.getElementById('evalFlags').textContent = data.red_flags || "A aguardar análise...";
            document.getElementById('evalCost').textContent = data.opportunity_cost || "A aguardar análise...";
            
            // status setup
            const badge = document.getElementById('evalStatusBadge');
            const actions = document.getElementById('actionButtons');
            
            if (data.status === "UNDER_ANALYSIS") {
                badge.textContent = "Em Análise";
                badge.className = "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide bg-blue-100 text-blue-800";
                actions.classList.remove('hidden'); 
            } else if (data.status === "APPROVED") {
                badge.textContent = "Aprovado";
                badge.className = "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide bg-green-100 text-green-800";
                actions.classList.add('hidden'); 
            } else {
                badge.textContent = "Descartado";
                badge.className = "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide bg-red-100 text-red-800";
                actions.classList.add('hidden'); 
            }

            panel.classList.remove('hidden');
        } else {
            throw new Error(data.detail || "Oportunidade não encontrada na base de dados.");
        }
    } catch (error) {
        errorMsg.textContent = error.message;
        errorMsg.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Pesquisar
        `;
    }
});

// Send the decision to the evaluator
async function sendFinalDecision(decision) {
    if (!currentOpportunityId) return;
    
    const actions = document.getElementById('actionButtons');
    const feedback = document.getElementById('actionFeedback');
    const badge = document.getElementById('evalStatusBadge');
    
    // hiddes the button
    actions.classList.add('hidden');
    
    try {
        const response = await fetch(`${API_URL}/${currentOpportunityId}/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ decision: decision })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            feedback.classList.remove('hidden');
            feedback.textContent = data.message;
            
            if (decision === 'APPROVED') {
                feedback.className = "p-4 rounded-lg text-center font-bold bg-green-100 text-green-800 border border-green-200 fade-in";
                badge.textContent = "Aprovado";
                badge.className = "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide bg-green-100 text-green-800";
            } else {
                feedback.className = "p-4 rounded-lg text-center font-bold bg-red-100 text-red-800 border border-red-200 fade-in";
                badge.textContent = "Descartado";
                badge.className = "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide bg-red-100 text-red-800";
            }
        } else {
            throw new Error(data.detail || "Falha ao gravar decisão.");
        }
    } catch (error) {
        alert(`Erro ao guardar a decisão: ${error.message}`);
        actions.classList.remove('hidden');
    }
}