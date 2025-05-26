// Mostrar/Ocultar senha
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

// Ocultar mensagens flash após 4 segundos
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(flash => {
    flash.style.transition = 'opacity 0.5s ease';
    flash.style.opacity = '0';
    setTimeout(() => flash.remove(), 500);
  });
}, 4000);
