#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arquivo de teste de performance para cenário de longa duração.
Simula uso contínuo do sistema por um longo período.
"""

from locust import HttpUser, task, between
import random
import json
from datetime import datetime, timedelta
import time

class UsuarioAutoCura(HttpUser):
    """Simula um usuário do sistema AutoCura em uso prolongado."""
    
    wait_time = between(2, 5)  # Tempo maior entre requisições
    
    def on_start(self):
        """Inicializa o usuário."""
        # Login inicial
        self.client.post(
            "/api/auth/login",
            json={
                "email": f"teste{random.randint(1, 100)}@autocura.com",
                "senha": "senha123"
            }
        )
    
    @task(5)
    def consultar_dashboard(self):
        """Consulta o dashboard principal."""
        self.client.get("/api/dashboard")
    
    @task(4)
    def listar_pacientes(self):
        """Lista pacientes cadastrados."""
        self.client.get("/api/pacientes")
    
    @task(3)
    def consultar_paciente(self):
        """Consulta dados de um paciente específico."""
        paciente_id = random.randint(1, 100)
        self.client.get(f"/api/pacientes/{paciente_id}")
    
    @task(3)
    def consultar_historico(self):
        """Consulta histórico de atendimentos."""
        self.client.get("/api/historico")
    
    @task(2)
    def consultar_estatisticas(self):
        """Consulta estatísticas do sistema."""
        self.client.get("/api/estatisticas")
    
    @task(2)
    def cadastrar_paciente(self):
        """Cadastra um novo paciente."""
        self.client.post(
            "/api/pacientes",
            json={
                "nome": f"Paciente Teste {random.randint(1, 100)}",
                "data_nascimento": (datetime.now() - timedelta(days=random.randint(1, 36500))).isoformat(),
                "email": f"paciente{random.randint(1, 100)}@teste.com",
                "telefone": f"1199999{random.randint(1000, 9999)}"
            }
        )
    
    @task(2)
    def atualizar_paciente(self):
        """Atualiza dados de um paciente."""
        paciente_id = random.randint(1, 100)
        self.client.put(
            f"/api/pacientes/{paciente_id}",
            json={
                "telefone": f"1199999{random.randint(1000, 9999)}",
                "endereco": f"Rua Teste {random.randint(1, 100)}"
            }
        )
    
    @task(1)
    def gerar_relatorio(self):
        """Gera um relatório personalizado."""
        self.client.post(
            "/api/relatorios",
            json={
                "tipo": random.choice(["diario", "semanal", "mensal"]),
                "periodo": {
                    "inicio": (datetime.now() - timedelta(days=30)).isoformat(),
                    "fim": datetime.now().isoformat()
                }
            }
        )
    
    @task(1)
    def backup_dados(self):
        """Realiza backup dos dados."""
        self.client.post(
            "/api/backup",
            json={
                "tipo": "completo",
                "destino": "nuvem"
            }
        )
    
    @task(1)
    def sincronizacao(self):
        """Sincroniza dados com sistemas externos."""
        self.client.post(
            "/api/sincronizacao",
            json={
                "sistemas": random.choice(["lab", "farmacia", "prontuario"]),
                "tipo": "incremental"
            }
        )
    
    @task(1)
    def manutencao(self):
        """Executa tarefas de manutenção."""
        self.client.post(
            "/api/manutencao",
            json={
                "tipo": random.choice(["limpeza", "otimizacao", "verificacao"]),
                "escopo": "sistema"
            }
        ) 