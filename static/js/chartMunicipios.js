document.addEventListener('DOMContentLoaded', function () {
    // Extrair labels e dados
    const labels = associadosPorMunicipio.map(item => item.municipio_circunscricao__municipio);
    const data = associadosPorMunicipio.map(item => item.associados_count);

    // Configurar o gráfico
    const ctx = document.getElementById('chartMunicipios').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut', // Altere para 'pie' ou 'polarArea' se preferir
        data: {
            labels: labels,
            datasets: [{
                label: 'Associados por Municípios',
                data: data,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
                ], // Cores dinâmicas para cada segmento
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
                        },
                    },
                },
            },
        },
    });
});
