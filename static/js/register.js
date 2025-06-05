const togglePassword = document.getElementById('toggle-password');
    const passwordField = document.getElementById('password');
    const eyeIcon = document.getElementById('eye-icon');

    if (togglePassword && passwordField && eyeIcon) {
      togglePassword.addEventListener('click', () => {
        const type = passwordField.type === 'password' ? 'text' : 'password';
        passwordField.type = type;

        eyeIcon.src = type === 'password' 
          ? 'static/img/eye-closed.png'  // olho branco aberto
          : 'static/img/eye-open.png';   // olho fechado

        eyeIcon.alt = type === 'password' 
          ? 'Olho Branco Aberto' 
          : 'Olho Fechado';
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
