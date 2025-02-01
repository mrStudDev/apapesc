document.addEventListener('DOMContentLoaded', function () {
    // Extrair labels e dados da variável global
    const labels = associadosPorReparticao.map(item => item.reparticao__nome_reparticao);
    const data = associadosPorReparticao.map(item => item.associados_count);

    // Configurar o gráfico
    const ctx = document.getElementById('chartReparticoes').getContext('2d');
    new Chart(ctx, {
        type: 'pie', // Altere para "polarArea" para outro estilo
        data: {
            labels: labels,
            datasets: [{
                label: 'Associados por Repartição',
                data: data,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
                ], // Cores para os segmentos
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function (tooltipItem) {
                            const total = tooltipItem.dataset.data.reduce((acc, val) => acc + val, 0);
                            const value = tooltipItem.raw;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${tooltipItem.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        },
    });
});
