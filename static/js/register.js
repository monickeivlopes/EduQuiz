document.addEventListener('DOMContentLoaded', () => {
  
  const togglePassword = document.getElementById('toggle-password');
  const passwordField = document.getElementById('password');
  const eyeIcon = document.getElementById('eye-icon');

  if (togglePassword && passwordField && eyeIcon) {
    togglePassword.addEventListener('click', () => {
      const type = passwordField.type === 'password' ? 'text' : 'password';
      passwordField.type = type;

      eyeIcon.src = type === 'password'
  ? "/static/img/eye-closed.png"
  : "/static/img/eye-open.png";

      eyeIcon.alt = type === 'password'
        ? "Olho fechado"
        : "Olho aberto";
    });
  }

  // Ocultar flash
  setTimeout(() => {
    document.querySelectorAll('.flash').forEach(flash => {
      flash.style.transition = 'opacity 0.5s ease';
      flash.style.opacity = '0';
      setTimeout(() => flash.remove(), 500);
    });
  }, 4000);

  // Mostrar ou ocultar curso conforme o tipo de usuário
  const tipoSelect = document.getElementById("tipo");
  const cursoSelect = document.getElementById("curso");

  tipoSelect.addEventListener('change', () => {
    if (tipoSelect.value === "aluno") {
      cursoSelect.style.display = "block";
      cursoSelect.disabled = false;
      cursoSelect.setAttribute("required", "required");
    } else {
      cursoSelect.style.display = "none";
      cursoSelect.disabled = true;
      cursoSelect.removeAttribute("required");
      cursoSelect.selectedIndex = 0;
    }
  });

  // Garante que o estado do select de curso está correto ao carregar
  if (tipoSelect.value === "aluno") {
    cursoSelect.style.display = "block";
    cursoSelect.disabled = false;
  } else {
    cursoSelect.style.display = "none";
    cursoSelect.disabled = true;
  }
});
