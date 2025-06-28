document.addEventListener("DOMContentLoaded", function () {
  // Modal do quiz (se existir)
  const modalQuiz = document.getElementById("modal-quiz");
  const btnIniciarQuiz = document.querySelector(".btn-iniciar");

  if (modalQuiz && btnIniciarQuiz) {
    const btnFecharQuiz = document.getElementById("fechar-modal");

    btnIniciarQuiz.addEventListener("click", () => {
      modalQuiz.style.display = "flex";
    });

    btnFecharQuiz?.addEventListener("click", () => {
      modalQuiz.style.display = "none";
    });

    window.addEventListener("click", function (event) {
      if (event.target == modalQuiz) {
        modalQuiz.style.display = "none";
      }
    });
  }

  // Modal de gerenciar questões (professor)
  const modalGerenciar = document.getElementById("modalGerenciar");

  if (modalGerenciar && btnIniciarQuiz) {
    btnIniciarQuiz.addEventListener("click", () => {
      modalGerenciar.style.display = "block";
    });

    window.addEventListener("click", function (event) {
      if (event.target === modalGerenciar) {
        modalGerenciar.style.display = "none";
      }
    });
  }
});

// Tornar a função global
function fecharModal() {
  const modal = document.getElementById("modalGerenciar");
  if (modal) modal.style.display = "none";
}
