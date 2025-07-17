
 function toggleGabarito() {
    const gabarito = document.getElementById("gabarito");
    const btn = event.target;
    if (gabarito.style.display === "none") {
      gabarito.style.display = "block";
      btn.textContent = "Ocultar Gabarito";
    } else {
      gabarito.style.display = "none";
      btn.textContent = "Ver Gabarito";
    }
  }
