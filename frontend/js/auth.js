document.getElementById('formLogin').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const pass = document.getElementById('adminPassword').value;
    const errorMsg = document.getElementById('loginError');
    
    // mmock validation
    if (pass === 'admin123') {
        errorMsg.classList.add('hidden');
        
        // redirects to the admin panel)
        window.location.href = 'dashboard.html';
    } else {
        // shows an error message
        errorMsg.classList.remove('hidden');
        document.getElementById('adminPassword').value = ''; 
    }
});