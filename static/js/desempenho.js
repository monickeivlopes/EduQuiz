document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById("graficoDesempenho").getContext("2d");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: Labels,
            datasets: [{
                label: "Acertos",
                data: Data,
                backgroundColor: "rgba(54, 162, 235, 0.5)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, // permite controlar altura via CSS
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Quantidade de Acertos"
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: "Data e Hora da Tentativa"
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: "Histórico de Acertos por Tentativa"
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Acertos: ${context.parsed.y}`;
                        }
                    }
                },
                legend: {
                    display: false
                }
            }
        }
    });
});
