#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arquivo de teste de performance para cenário de carga baixa.
Simula usuários acessando o sistema com carga mínima.
"""

from locust import HttpUser, task, between
import random
import json

class UsuarioAutoCura(HttpUser):
    """Simula um usuário do sistema AutoCura."""
    
    wait_time = between(1, 3)  # Tempo entre requisições
    
    def on_start(self):
        """Inicializa o usuário."""
        # Login inicial
        self.client.post(
            "/api/auth/login",
            json={
                "email": "teste@autocura.com",
                "senha": "senha123"
            }
        )
    
    @task(3)
    def consultar_dashboard(self):
        """Consulta o dashboard principal."""
        self.client.get("/api/dashboard")
    
    @task(2)
    def listar_pacientes(self):
        """Lista pacientes cadastrados."""
        self.client.get("/api/pacientes")
    
    @task(1)
    def consultar_paciente(self):
        """Consulta dados de um paciente específico."""
        paciente_id = random.randint(1, 100)
        self.client.get(f"/api/pacientes/{paciente_id}")
    
    @task(1)
    def consultar_historico(self):
        """Consulta histórico de atendimentos."""
        self.client.get("/api/historico")
    
    @task(1)
    def consultar_estatisticas(self):
        """Consulta estatísticas do sistema."""
        self.client.get("/api/estatisticas") 