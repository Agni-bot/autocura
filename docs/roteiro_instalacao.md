# Roteiro para Scripts de Instalação Modularizados

Este documento descreve o roteiro e o propósito de cada script de instalação a ser criado.

## Etapas de Instalação e Scripts Correspondentes:

1.  **`01_validar_ambiente.sh`**: 
    *   **Propósito**: Realizar verificações prévias no sistema para garantir que o ambiente é compatível e possui os pré-requisitos mínimos.
    *   **Ações**: Verificar tipo de SO, arquitetura, permissões de execução, espaço em disco disponível, conectividade básica com a internet (se necessário para etapas futuras).

2.  **`02_instalar_dependencias.sh`**: 
    *   **Propósito**: Instalar todos os pacotes de software e bibliotecas dos quais o sistema principal depende.
    *   **Ações**: Atualizar listas de pacotes (ex: `apt-get update`), instalar pacotes via gerenciador (ex: `apt-get install -y curl wget jq`), verificar se a instalação dos pacotes foi bem-sucedida.

3.  **`03_configurar_usuarios_grupos.sh`**: 
    *   **Propósito**: Criar usuários e grupos dedicados para a aplicação, se necessário, para fins de segurança e isolamento.
    *   **Ações**: Verificar se o usuário/grupo já existe; criar usuário do sistema (ex: `useradd -r -s /bin/false appuser`); criar grupo (ex: `groupadd appgroup`); adicionar usuário ao grupo.

4.  **`04_criar_diretorios.sh`**: 
    *   **Propósito**: Preparar a estrutura de diretórios necessária para a instalação e operação do sistema.
    *   **Ações**: Definir diretórios base (ex: `/opt/meuapp`, `/var/log/meuapp`, `/etc/meuapp`); criar os diretórios com `mkdir -p`; definir permissões e propriedade corretas para os diretórios (ex: `chown appuser:appgroup /opt/meuapp`).

5.  **`05_baixar_artefatos_aplicacao.sh`**: 
    *   **Propósito**: Baixar os binários, pacotes ou código-fonte da aplicação a ser instalada.
    *   **Ações**: Usar `wget` ou `curl` para baixar de uma URL; verificar a integridade do arquivo baixado (ex: checksum); extrair o conteúdo se for um arquivo compactado (ex: `tar -xzf`).

6.  **`06_configurar_aplicacao.sh`**: 
    *   **Propósito**: Configurar a aplicação com base em templates ou configurações padrão, ajustando para o ambiente específico.
    *   **Ações**: Copiar arquivos de configuração de exemplo para os locais corretos; substituir placeholders em arquivos de configuração (ex: usando `sed` ou variáveis de ambiente); configurar conexões com banco de dados, portas de serviço, etc.

7.  **`07_inicializar_servicos.sh`**: 
    *   **Propósito**: Configurar e iniciar os serviços ou daemons da aplicação.
    *   **Ações**: Se for um serviço systemd, criar/copiar o arquivo de unit (ex: `/etc/systemd/system/meuapp.service`); recarregar o daemon do systemd (`systemctl daemon-reload`); habilitar o serviço para iniciar no boot (`systemctl enable meuapp`); iniciar o serviço (`systemctl start meuapp`); verificar o status do serviço (`systemctl is-active meuapp`).

8.  **`08_validacao_pos_instalacao.sh`**: 
    *   **Propósito**: Realizar verificações básicas para confirmar que a aplicação foi instalada e está funcionando corretamente.
    *   **Ações**: Testar se a aplicação responde em uma porta específica (ex: `curl localhost:8080/health`); verificar logs iniciais por erros; executar um comando básico da aplicação que indique sucesso.

9.  **`09_limpeza_instalacao.sh`**: 
    *   **Propósito**: Remover arquivos temporários de instalação que não são mais necessários.
    *   **Ações**: Remover arquivos baixados, diretórios de extração temporários, etc.

## Arquivo de Controle de Fluxo (Flag Files)

Cada script, ao ser concluído com sucesso, criará um arquivo de flag no diretório de instalação ou em `/tmp` para indicar sua conclusão. Por exemplo:
*   `01_validar_ambiente.sh` cria `.etapa_01_ok`
*   `02_instalar_dependencias.sh` cria `.etapa_02_ok`
*   E assim por diante.

O script subsequente verificará a existência do arquivo de flag da etapa anterior antes de prosseguir.

## Script Principal (Opcional)

Um script principal `install_all.sh` pode ser criado para orquestrar a execução de todos os scripts em sequência, verificando os flags.

