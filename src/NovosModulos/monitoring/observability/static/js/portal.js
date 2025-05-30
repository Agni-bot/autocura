// Portal Central - Sistema de Autocura Cognitiva
document.addEventListener('DOMContentLoaded', function() {
    // Inicialização
    initializeTheme();
    loadAllData();
    setupEventListeners();
});

// Gerenciamento de Tema
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButton(newTheme);
}

function updateThemeButton(theme) {
    const button = document.querySelector('[onclick="toggleTheme()"] i');
    button.className = theme === 'light' ? 'bi bi-moon' : 'bi bi-sun';
}

// Carregamento de Dados
function loadAllData() {
    loadSystemSummary();
    loadWillData();
    loadMetrics();
    loadDiagnostics();
    loadActions();
    loadServices();
    loadLogs();
}

function loadSystemSummary() {
    fetch('/api/v1/summary')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('resumo-sistema');
            container.innerHTML = `
                <div class="row">
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div class="metric-value">${data.active_services}</div>
                            <div class="metric-label">Serviços Ativos</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div class="metric-value">${data.active_alerts}</div>
                            <div class="metric-label">Alertas Ativos</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div class="metric-value">${data.pending_actions}</div>
                            <div class="metric-label">Ações Pendentes</div>
                        </div>
                    </div>
                </div>
            `;
        })
        .catch(error => {
            console.error('Erro ao carregar resumo:', error);
            document.getElementById('resumo-sistema').innerHTML = 
                '<div class="alert alert-danger">Erro ao carregar resumo do sistema</div>';
        });
}

function loadWillData() {
    fetch('/api/will/status')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('will-content');
            container.innerHTML = `
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Status do Will</h5>
                        <p class="card-text">Estado: ${data.status}</p>
                        <p class="card-text">Última decisão: ${data.last_decision}</p>
                        <p class="card-text">Confiança: ${data.confidence}%</p>
                    </div>
                </div>
            `;
        })
        .catch(error => {
            console.error('Erro ao carregar dados do Will:', error);
            document.getElementById('will-content').innerHTML = 
                '<div class="alert alert-danger">Erro ao carregar dados do Will</div>';
        });
}

function loadMetrics() {
    fetch('/api/v1/metrics')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('metricas-content');
            container.innerHTML = `
                <div class="row">
                    ${data.metrics.map(metric => `
                        <div class="col-md-4 mb-4">
                            <div class="metric-card">
                                <div class="metric-value">${metric.value}</div>
                                <div class="metric-label">${metric.name}</div>
                                <div class="metric-trend ${metric.trend > 0 ? 'text-success' : 'text-danger'}">
                                    <i class="bi bi-arrow-${metric.trend > 0 ? 'up' : 'down'}"></i>
                                    ${Math.abs(metric.trend)}%
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        })
        .catch(error => {
            console.error('Erro ao carregar métricas:', error);
            document.getElementById('metricas-content').innerHTML = 
                '<div class="alert alert-danger">Erro ao carregar métricas</div>';
        });
}

function loadDiagnostics() {
    fetch('/api/v1/diagnostics')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('diagnosticos-content');
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Serviço</th>
                                <th>Status</th>
                                <th>Última Verificação</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.diagnostics.map(diag => `
                                <tr>
                                    <td>${diag.id}</td>
                                    <td>${diag.service}</td>
                                    <td>
                                        <span class="badge bg-${diag.status === 'OK' ? 'success' : 'danger'}">
                                            ${diag.status}
                                        </span>
                                    </td>
                                    <td>${new Date(diag.last_check).toLocaleString()}</td>
                                    <td>
                                        <button class="btn btn-sm btn-primary" 
                                                onclick="viewDiagnostic(${diag.id})">
                                            <i class="bi bi-eye"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        })
        .catch(error => {
            console.error('Erro ao carregar diagnósticos:', error);
            document.getElementById('diagnosticos-content').innerHTML = 
                '<div class="alert alert-danger">Erro ao carregar diagnósticos</div>';
        });
}

function loadActions() {
    fetch('/api/v1/actions')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('acoes-content');
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Tipo</th>
                                <th>Status</th>
                                <th>Data</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.actions.map(action => `
                                <tr>
                                    <td>${action.id}</td>
                                    <td>${action.type}</td>
                                    <td>
                                        <span class="badge bg-${getStatusColor(action.status)}">
                                            ${action.status}
                                        </span>
                                    </td>
                                    <td>${new Date(action.date).toLocaleString()}</td>
                                    <td>
                                        <button class="btn btn-sm btn-primary" 
                                                onclick="viewAction(${action.id})">
                                            <i class="bi bi-eye"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        })
        .catch(error => {
            console.error('Erro ao carregar ações:', error);
            document.getElementById('acoes-content').innerHTML = 
                '<div class="alert alert-danger">Erro ao carregar ações</div>';
        });
}

function loadServices() {
    fetch('/api/v1/services')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('servicos-content');
            container.innerHTML = `
                <div class="row">
                    ${data.services.map(service => `
                        <div class="col-md-4 mb-4">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">${service.name}</h5>
                                    <p class="card-text">
                                        Status: 
                                        <span class="badge bg-${service.status === 'running' ? 'success' : 'danger'}">
                                            ${service.status}
                                        </span>
                                    </p>
                                    <p class="card-text">
                                        <small class="text-muted">
                                            Última atualização: ${new Date(service.last_update).toLocaleString()}
                                        </small>
                                    </p>
                                    <div class="btn-group">
                                        <button class="btn btn-sm btn-primary" 
                                                onclick="viewService('${service.name}')">
                                            <i class="bi bi-eye"></i> Detalhes
                                        </button>
                                        <button class="btn btn-sm btn-${service.status === 'running' ? 'danger' : 'success'}"
                                                onclick="toggleService('${service.name}')">
                                            <i class="bi bi-${service.status === 'running' ? 'stop' : 'play'}"></i>
                                            ${service.status === 'running' ? 'Parar' : 'Iniciar'}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        })
        .catch(error => {
            console.error('Erro ao carregar serviços:', error);
            document.getElementById('servicos-content').innerHTML = 
                '<div class="alert alert-danger">Erro ao carregar serviços</div>';
        });
}

function loadLogs() {
    fetch('/api/v1/logs')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('logs-content');
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Serviço</th>
                                <th>Nível</th>
                                <th>Mensagem</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.logs.map(log => `
                                <tr>
                                    <td>${new Date(log.timestamp).toLocaleString()}</td>
                                    <td>${log.service}</td>
                                    <td>
                                        <span class="badge bg-${getLogLevelColor(log.level)}">
                                            ${log.level}
                                        </span>
                                    </td>
                                    <td>${log.message}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        })
        .catch(error => {
            console.error('Erro ao carregar logs:', error);
            document.getElementById('logs-content').innerHTML = 
                '<div class="alert alert-danger">Erro ao carregar logs</div>';
        });
}

// Funções Auxiliares
function getStatusColor(status) {
    const colors = {
        'pending': 'warning',
        'running': 'info',
        'completed': 'success',
        'failed': 'danger'
    };
    return colors[status] || 'secondary';
}

function getLogLevelColor(level) {
    const colors = {
        'INFO': 'info',
        'WARNING': 'warning',
        'ERROR': 'danger',
        'DEBUG': 'secondary'
    };
    return colors[level] || 'secondary';
}

// Event Listeners
function setupEventListeners() {
    // Busca Global
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value.toLowerCase();
            searchAllSections(query);
        }, 300));
    }

    // Navegação
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            scrollToSection(targetId);
        });
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function searchAllSections(query) {
    const sections = document.querySelectorAll('.doc-section');
    sections.forEach(section => {
        const content = section.textContent.toLowerCase();
        section.style.display = content.includes(query) ? 'block' : 'none';
    });
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
        // Atualiza link ativo
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${sectionId}`) {
                link.classList.add('active');
            }
        });
    }
}

// Funções de Atualização
function refreshAll() {
    const button = document.querySelector('[onclick="refreshAll()"]');
    button.disabled = true;
    button.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Atualizando...';
    
    loadAllData();
    
    setTimeout(() => {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Atualizar';
    }, 1000);
}

// Funções de Visualização
function viewDiagnostic(id) {
    fetch(`/api/v1/diagnostics/${id}`)
        .then(response => response.json())
        .then(data => {
            // Implementar modal ou página de detalhes
            console.log('Detalhes do diagnóstico:', data);
        })
        .catch(error => console.error('Erro ao carregar diagnóstico:', error));
}

function viewAction(id) {
    fetch(`/api/v1/actions/${id}`)
        .then(response => response.json())
        .then(data => {
            // Implementar modal ou página de detalhes
            console.log('Detalhes da ação:', data);
        })
        .catch(error => console.error('Erro ao carregar ação:', error));
}

function viewService(name) {
    fetch(`/api/v1/services/${name}`)
        .then(response => response.json())
        .then(data => {
            // Implementar modal ou página de detalhes
            console.log('Detalhes do serviço:', data);
        })
        .catch(error => console.error('Erro ao carregar serviço:', error));
}

function toggleService(name) {
    fetch(`/api/v1/services/${name}/toggle`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            loadServices(); // Recarrega a lista de serviços
        })
        .catch(error => console.error('Erro ao alternar serviço:', error));
}

// Função para alternar sidebar em dispositivos móveis
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const content = document.querySelector('.content');
    sidebar.classList.toggle('active');
    content.classList.toggle('active');
} 