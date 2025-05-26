// Abrir modal de login ao clicar no botão
const loginBtn = document.querySelector('.login');
const modal = document.getElementById('loginModal');

if (loginBtn && modal) {
  loginBtn.addEventListener('click', () => {
    modal.style.display = 'flex';
  });

  // Fechar modal ao clicar fora dele
  window.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
    }
  });
}

// Mostrar/Ocultar senha no login
const togglePassword = document.getElementById('toggle-password');
const passwordField = document.getElementById('password');
const eyeIcon = document.getElementById('eye-icon');

if (togglePassword && passwordField && eyeIcon) {
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
}

// Reabrir modal de login automaticamente se houver erro
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('abrir_login') === '1' && modal) {
  modal.style.display = 'flex';
}

// Ocultar mensagens flash após 4 segundos
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(flash => {
    flash.style.transition = 'opacity 0.5s ease';
    flash.style.opacity = '0';
    setTimeout(() => flash.remove(), 500);
  });
}, 4000);
