document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("modal-quiz");
  const btnIniciar = document.querySelector(".btn-iniciar");
  const btnFechar = document.getElementById("fechar-modal");

  btnIniciar.addEventListener("click", () => {
    modal.style.display = "flex";
  });

  btnFechar.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };
});

/* Script prof */

  const modal = document.getElementById("modalGerenciar");
  const botaoAbrir = document.querySelector(".btn-iniciar");

  botaoAbrir.addEventListener("click", () => {
    modal.style.display = "block";
  });

  function fecharModal() {
    modal.style.display = "none";
  }

  window.onclick = function(event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  }

