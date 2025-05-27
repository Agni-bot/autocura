from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """View para renderizar o dashboard principal."""
    return render(request, 'observabilidade/dashboard.html')

@login_required
def dashboard_data(request):
    """API endpoint para fornecer dados do dashboard."""
    # TODO: Implementar lógica real de coleta de dados
    data = {
        'status_sistema': 'Operacional',
        'acoes_pendentes': 5,
        'alertas_ativos': 2,
        'metricas_performance': '95%',
        'metricas': {
            'labels': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            'valores': [65, 59, 80, 81, 56, 55]
        },
        'alertas': {
            'labels': ['Crítico', 'Alto', 'Médio', 'Baixo'],
            'valores': [2, 5, 8, 3]
        },
        'acoes_recentes': [
            {
                'id': 1,
                'tipo': 'Manutenção',
                'descricao': 'Atualização de segurança',
                'status': 'Concluído',
                'data': '2024-03-20'
            },
            {
                'id': 2,
                'tipo': 'Backup',
                'descricao': 'Backup diário',
                'status': 'Pendente',
                'data': '2024-03-21'
            }
        ]
    }
    return JsonResponse(data) 