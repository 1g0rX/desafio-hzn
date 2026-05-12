const API_URL = "http://localhost:8000/api/opportunities";

document.getElementById('formSubmission').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btn = document.getElementById('btnSubmit');
    const alertBox = document.getElementById('submissionAlert');
    const alertTitle = document.getElementById('submissionAlertTitle');
    const alertText = document.getElementById('submissionAlertText');
    
    // button status
    btn.disabled = true;
    btn.textContent = 'Enviando para a IA... aguarde';
    
    // hides the alert before a new attemp
    alertBox.classList.add('hidden');
    alertBox.classList.remove('flex', 'bg-green-50', 'text-green-800', 'bg-red-50', 'text-red-800');

    const formData = new FormData();
    formData.append("name", document.getElementById('propName').value);
    formData.append("email", document.getElementById('propEmail').value);
    formData.append("phone", document.getElementById('propPhone').value);
    formData.append("file", document.getElementById('propFile').files[0]);

    try {
        const response = await fetch(`${API_URL}/submit`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // success feedback
            alertBox.classList.add('flex', 'bg-green-50', 'text-green-800', 'border', 'border-green-200');
            alertTitle.textContent = "Ideia Submetida com Sucesso!";
            alertText.innerHTML = `${data.message}<br><br><strong>O seu ID de acompanhamento é: #${data.id}</strong>`;
            document.getElementById('formSubmission').reset();
        } else {
            throw new Error(data.detail || "Erro desconhecido ao comunicar com o servidor.");
        }
    } catch (error) {
        // error feedback
        alertBox.classList.add('flex', 'bg-red-50', 'text-red-800', 'border', 'border-red-200');
        alertTitle.textContent = "Falha no Envio";
        alertText.textContent = error.message;
    } finally {
        // restore button
        btn.disabled = false;
        btn.textContent = 'Submeter para Análise';
        alertBox.classList.remove('hidden');
    }
});