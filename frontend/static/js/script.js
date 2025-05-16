document.addEventListener('DOMContentLoaded', function() {
    const servicesGrid = document.getElementById('services-grid');

    // Dados mockados dos serviços. No futuro, isso viria de uma API.
    const services = [
        {
            id: 'diagnostico_cognitivo',
            name: 'Diagnóstico Cognitivo',
            description: 'Módulo para identificar e analisar falhas cognitivas no sistema.',
            link: '#/services/diagnostico'
        },
        {
            id: 'autocorrecao_avancada',
            name: 'Autocorreção Avançada',
            description: 'Implementa mecanismos de correção autônoma para falhas detectadas.',
            link: '#/services/autocorrecao'
        },
        {
            id: 'adaptacao_autonoma',
            name: 'Adaptação Autônoma',
            description: 'Permite que o sistema se adapte a novas situações e ambientes.',
            link: '#/services/adaptacao'
        },
        {
            id: 'previsao_cenarios',
            name: 'Previsão de Cenários',
            description: 'Analisa dados para prever cenários econômicos, políticos e históricos.',
            link: '#/services/previsao'
        },
        {
            id: 'consciencia_situacional',
            name: 'Consciência Situacional',
            description: 'Monitora e analisa o ambiente operacional em tempo real.',
            link: '#/services/consciencia'
        },
        {
            id: 'financas_autocura',
            name: 'Finanças Autocura',
            description: 'Microsserviço para gestão financeira, trading e crowdfunding.',
            link: '#/services/financas' // Ou um link externo se for um serviço separado
        }
    ];

    function loadServices() {
        if (!servicesGrid) {
            console.error('Elemento services-grid não encontrado.');
            return;
        }

        servicesGrid.innerHTML = ''; // Limpa o grid antes de adicionar novos cards

        services.forEach(service => {
            const card = document.createElement('div');
            card.className = 'service-card';
            card.innerHTML = `
                <h3>${service.name}</h3>
                <p>${service.description}</p>
                <a href="${service.link}" class="service-link" data-service-id="${service.id}">Acessar Módulo</a>
            `;
            servicesGrid.appendChild(card);
        });

        // Adicionar event listeners para os links (exemplo)
        document.querySelectorAll('.service-link').forEach(link => {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                const serviceId = this.getAttribute('data-service-id');
                alert(`Redirecionando para o serviço: ${serviceId}. Em uma aplicação real, aqui ocorreria a navegação ou chamada da funcionalidade.`);
                // Exemplo: window.location.href = this.href;
            });
        });
    }

    // Carrega os serviços quando a página estiver pronta
    loadServices();

    // Futuramente, poderia haver uma função para buscar serviços de uma API:
    // async function fetchServices() {
    //     try {
    //         const response = await fetch('/api/services'); // Endpoint do backend Flask
    //         if (!response.ok) {
    //             throw new Error(`HTTP error! status: ${response.status}`);
    //         }
    //         const servicesData = await response.json();
    //         // Atualizar a variável 'services' e chamar loadServices()
    //     } catch (error) {
    //         console.error('Falha ao buscar serviços:', error);
    //         servicesGrid.innerHTML = '<p>Erro ao carregar serviços. Tente novamente mais tarde.</p>';
    //     }
    // }
    // fetchServices();
});
