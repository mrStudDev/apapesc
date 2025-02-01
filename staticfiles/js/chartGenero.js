document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('chart2').getContext('2d');

    // Configuração do gráfico
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Masculino', 'Feminino', 'Indefinido'],
            datasets: [{
                label: 'Associados por Gênero',
                data: [associadosHomens, associadosMulheres, associadosIndefinidos],
                backgroundColor: ['#4F46E5', '#EC4899', '#9CA3AF'],
                borderWidth: 1,
            }]
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
        }
    });
});
