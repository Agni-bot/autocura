#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arquivo de teste de performance para cenário de estresse.
Simula condições extremas de uso do sistema.
"""

from locust import HttpUser, task, between
import random
import json
from datetime import datetime, timedelta
import time

class UsuarioAutoCura(HttpUser):
    """Simula um usuário do sistema AutoCura sob condições de estresse."""
    
    wait_time = between(0.1, 0.5)  # Tempo mínimo entre requisições
    
    def on_start(self):
        """Inicializa o usuário."""
        # Login inicial
        self.client.post(
            "/api/auth/login",
            json={
                "email": f"teste{random.randint(1, 10000)}@autocura.com",
                "senha": "senha123"
            }
        )
    
    @task(10)
    def consultar_dashboard(self):
        """Consulta o dashboard principal."""
        self.client.get("/api/dashboard")
    
    @task(8)
    def listar_pacientes(self):
        """Lista pacientes cadastrados."""
        self.client.get("/api/pacientes")
    
    @task(6)
    def consultar_paciente(self):
        """Consulta dados de um paciente específico."""
        paciente_id = random.randint(1, 10000)
        self.client.get(f"/api/pacientes/{paciente_id}")
    
    @task(6)
    def consultar_historico(self):
        """Consulta histórico de atendimentos."""
        self.client.get("/api/historico")
    
    @task(4)
    def consultar_estatisticas(self):
        """Consulta estatísticas do sistema."""
        self.client.get("/api/estatisticas")
    
    @task(4)
    def cadastrar_paciente(self):
        """Cadastra um novo paciente."""
        self.client.post(
            "/api/pacientes",
            json={
                "nome": f"Paciente Teste {random.randint(1, 10000)}",
                "data_nascimento": (datetime.now() - timedelta(days=random.randint(1, 36500))).isoformat(),
                "email": f"paciente{random.randint(1, 10000)}@teste.com",
                "telefone": f"1199999{random.randint(1000, 9999)}"
            }
        )
    
    @task(4)
    def atualizar_paciente(self):
        """Atualiza dados de um paciente."""
        paciente_id = random.randint(1, 10000)
        self.client.put(
            f"/api/pacientes/{paciente_id}",
            json={
                "telefone": f"1199999{random.randint(1000, 9999)}",
                "endereco": f"Rua Teste {random.randint(1, 10000)}"
            }
        )
    
    @task(3)
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
    
    @task(2)
    def upload_arquivo(self):
        """Faz upload de um arquivo grande."""
        # Gera um arquivo de 1MB com dados aleatórios
        dados = b"0" * 1024 * 1024
        self.client.post(
            "/api/arquivos/upload",
            files={"arquivo": ("teste.txt", dados)}
        )
    
    @task(2)
    def consulta_complexa(self):
        """Executa uma consulta complexa."""
        self.client.post(
            "/api/consultas/complexas",
            json={
                "filtros": {
                    "data_inicio": (datetime.now() - timedelta(days=365)).isoformat(),
                    "data_fim": datetime.now().isoformat(),
                    "tipo_atendimento": random.choice(["emergencia", "consulta", "exame"]),
                    "status": random.choice(["pendente", "concluido", "cancelado"])
                },
                "agrupamentos": ["data", "tipo", "status"],
                "ordenacao": ["data", "desc"]
            }
        )
    
    @task(1)
    def operacao_lenta(self):
        """Executa uma operação que consome muitos recursos."""
        self.client.post(
            "/api/operacoes/lentas",
            json={
                "tipo": "processamento_lote",
                "dados": [random.randint(1, 1000000) for _ in range(1000)]
            }
        ) 