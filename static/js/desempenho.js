document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById("graficoDesempenho").getContext("2d");

    const grafico = new Chart(ctx, {
        type: "bar", // Pode trocar para 'line' se preferir
        data: {
            labels: Labels,
            datasets: [{
                label: "Acertos por Tentativa",
                data: Data,
                borderWidth: 1,
                backgroundColor: "rgba(54, 162, 235, 0.5)", // azul claro
                borderColor: "rgba(54, 162, 235, 1)"
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Acertos'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Data e Hora da Tentativa'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Histórico de Acertos'
                },
                legend: {
                    display: false
                }
            }
        }
    });
});
