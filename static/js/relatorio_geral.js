document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("studentsTable");
    const headers = table.querySelectorAll("th");
    let sortDirection = 1;

    // ------------------ ORDENAR TABELA ------------------
    headers.forEach(header => {
        header.addEventListener("click", function () {
            const index = Array.from(headers).indexOf(this);
            const rows = Array.from(table.querySelector("tbody").querySelectorAll("tr"));

            rows.sort((a, b) => {
                const aText = a.querySelectorAll("td")[index].textContent.trim();
                const bText = b.querySelectorAll("td")[index].textContent.trim();

                if (!isNaN(parseFloat(aText)) && !isNaN(parseFloat(bText))) {
                    return (parseFloat(aText) - parseFloat(bText)) * sortDirection;
                }
                return aText.localeCompare(bText) * sortDirection;
            });

            sortDirection *= -1;

            const tbody = table.querySelector("tbody");
            tbody.innerHTML = "";
            rows.forEach(row => tbody.appendChild(row));

            headers.forEach(h => h.textContent = h.textContent.replace("▲", "").replace("▼", ""));
            this.textContent += sortDirection === 1 ? " ▲" : " ▼";
        });
    });

    // ------------------ FILTROS E BUSCA ------------------
    const filterCurso = document.getElementById("filterCurso");
    const filterPerformance = document.getElementById("filterPerformance");
    const searchInput = document.getElementById("searchInput");

    filterCurso.addEventListener("change", filterTable);
    filterPerformance.addEventListener("change", filterTable);
    searchInput.addEventListener("input", filterTable);

    function filterTable() {
        const cursoValue = filterCurso.value.toLowerCase();
        const perfValue = filterPerformance.value;
        const searchValue = searchInput.value.toLowerCase();
        const rows = table.querySelectorAll("tbody tr");

        rows.forEach(row => {
            const curso = row.querySelector("td:nth-child(2)").textContent.toLowerCase();
            const performance = parseFloat(row.querySelector("td:nth-child(4)").textContent.replace('%',''));
            const nome = row.querySelector("td:first-child").textContent.toLowerCase();

            let show = true;

            // Filtrar curso
            if(cursoValue !== "all" && curso !== cursoValue) show = false;

            // Filtrar performance
            switch(perfValue) {
                case "90": if(performance < 90) show = false; break;
                case "70": if(performance < 70 || performance >= 90) show = false; break;
                case "50": if(performance < 50 || performance >= 70) show = false; break;
                case "0": if(performance >= 50) show = false; break;
            }

            // Filtrar nome
            if(!nome.includes(searchValue)) show = false;

            row.style.display = show ? "" : "none";
        });
    }

   // ------------------ GRÁFICO DE DESEMPENHO ------------------
if (Array.isArray(Labels) && Array.isArray(Data) && Labels.length > 0 && Data.length > 0) {
    const ctx = document.getElementById("performanceChart").getContext("2d");
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
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "Quantidade de Acertos" },
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    title: { display: true, text: "Aluno - Data" },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            plugins: {
                title: { display: true, text: "Top 10 Alunos por Acertos" },
                legend: { display: false }
            }
        }
    });
}

// ------------------ GRÁFICO DE MÉDIAS POR CURSO ------------------
if (Array.isArray(CursosLabels) && Array.isArray(CursosData) && CursosLabels.length > 0) {
    const ctxPie = document.getElementById("courseChart").getContext("2d");
    new Chart(ctxPie, {
        type: "bar",  // Mudei para barra para melhor visualização de médias
        data: {
            labels: CursosLabels,
            datasets: [{
                label: "Média de Acertos (%)",
                data: CursosData,
                backgroundColor: [
                    "#36A2EB", "#FF6384", "#4BC0C0", "#FF9F40", "#9966FF"
                ]
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: "Percentual de Acertos" }
                }
            },
            plugins: {
                title: { display: true, text: "Desempenho por Curso" }
            }
        }
    });
}
})

// ------------------ GRÁFICO DE ACERTOS X ERROS (se necessário) ------------------
// Este gráfico pode ser opcional, dependendo dos dados disponíveis