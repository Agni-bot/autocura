// Função para atualizar os dados do dashboard
function atualizarDashboard() {
    fetch('/api/observabilidade/dashboard')
        .then(response => response.json())
        .then(data => {
            // Atualizar cards
            document.getElementById('status-sistema').textContent = data.status_sistema;
            document.getElementById('acoes-pendentes').textContent = data.acoes_pendentes;
            document.getElementById('alertas-ativos').textContent = data.alertas_ativos;
            document.getElementById('metricas-performance').textContent = data.metricas_performance;

            // Atualizar gráficos
            atualizarGraficoMetricas(data.metricas);
            atualizarGraficoAlertas(data.alertas);

            // Atualizar tabela de ações
            const tbody = document.getElementById('acoes-recentes');
            tbody.innerHTML = '';
            
            data.acoes_recentes.forEach(acao => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${acao.id}</td>
                    <td>${acao.tipo}</td>
                    <td>${acao.descricao}</td>
                    <td><span class="badge badge-${acao.status === 'Concluído' ? 'success' : 'warning'}">${acao.status}</span></td>
                    <td>${acao.data}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Erro ao atualizar dashboard:', error);
            alert('Erro ao carregar dados do dashboard. Por favor, tente novamente.');
        });
}

// Função para atualizar o gráfico de métricas
function atualizarGraficoMetricas(dados) {
    const ctx = document.getElementById('grafico-metricas').getContext('2d');
    
    if (window.metricasChart) {
        window.metricasChart.destroy();
    }

    window.metricasChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dados.labels,
            datasets: [{
                label: 'Performance',
                data: dados.valores,
                borderColor: '#4e73df',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Função para atualizar o gráfico de alertas
function atualizarGraficoAlertas(dados) {
    const ctx = document.getElementById('grafico-alertas').getContext('2d');
    
    if (window.alertasChart) {
        window.alertasChart.destroy();
    }

    window.alertasChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dados.labels,
            datasets: [{
                label: 'Alertas',
                data: dados.valores,
                backgroundColor: '#f6c23e'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Atualizar dashboard a cada 30 segundos
setInterval(atualizarDashboard, 30000);

// Atualizar dashboard ao carregar a página
document.addEventListener('DOMContentLoaded', atualizarDashboard); 