# Sistema Autocura

Sistema de Inteligência Artificial com capacidades de autocura e evolução contínua.

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- Docker e Docker Compose
- PowerShell (Windows) ou Bash (Linux/macOS)
- Git

### Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/autocura.git
cd autocura
```

2. Instale as dependências:
```powershell
# Windows (PowerShell)
.\scripts\autocura.ps1 -Action install

# Linux/macOS (Bash)
./scripts/autocura.sh install
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### Instalação via Docker

```bash
docker-compose up -d
```

## 🛠️ Uso

### Comandos Básicos

```powershell
# Windows (PowerShell)
.\scripts\autocura.ps1 -Action <ação>

# Linux/macOS (Bash)
./scripts/autocura.sh <ação>
```

Ações disponíveis:
- `install`: Instala dependências
- `test`: Executa testes
- `lint`: Verifica código
- `build`: Constrói imagens Docker
- `clean`: Limpa arquivos temporários
- `monitor`: Inicia monitoramento
- `backup`: Realiza backup
- `restore`: Restaura backup

### Monitoramento

O sistema inclui integração com:
- Prometheus (métricas)
- Grafana (visualização)
- Logs estruturados

Acesse:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=src tests/ --cov-report=html
```

## 📚 Documentação

A documentação completa está disponível em:
- [Arquitetura](docs/arquitetura_integrada.txt)
- [Módulos](docs/modulos_funcionais.md)
- [Ética](docs/detalhamento_modulos_eticos.md)
- [Interfaces](docs/interfaces_tecnologias.md)

## 🔒 Segurança

O sistema implementa:
- Validação de entrada/saída
- Logging seguro
- Anonimização de dados
- Controle de acesso
- Criptografia em trânsito e repouso

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Para suporte, abra uma issue no GitHub ou contate a equipe de desenvolvimento. 