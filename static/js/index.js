
    const loginBtn = document.querySelector('.login');
    const modal = document.getElementById('loginModal');

    loginBtn.addEventListener('click', () => {
        modal.style.display = 'flex';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    const togglePassword = document.getElementById('toggle-password');
    const passwordField = document.getElementById('password');
    const eyeIcon = document.getElementById('eye-icon');

    togglePassword.addEventListener('click', () => {
        const type = passwordField.type === 'password' ? 'text' : 'password';
        passwordField.type = type;

        eyeIcon.src = type === 'password' 
            ? 'static/img/eye-closed.png' 
            : 'static/img/eye-open.png';
        eyeIcon.alt = type === 'password' 
            ? 'Olho Fechado' 
            : 'Olho Aberto';
    });
