document.addEventListener('DOMContentLoaded', function () {
    // Extrair labels e dados
    const labels = associadosPorStatus.map(item => item.status);
    const data = associadosPorStatus.map(item => item.count);

    // Configurar o gráfico
    const ctx = document.getElementById('chartStatus').getContext('2d');
    new Chart(ctx, {
        type: 'pie', // Alterne para 'bar', 'doughnut', ou outros tipos, se necessário
        data: {
            labels: labels,
            datasets: [{
                label: 'Associados Por Status',
                data: data,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
                ],
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
