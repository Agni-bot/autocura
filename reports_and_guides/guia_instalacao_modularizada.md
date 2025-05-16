# Guia de Instalação Modularizada

Este guia descreve a série de scripts de instalação modularizados projetados para instalar e configurar uma aplicação de forma sequencial e controlada. Cada script representa uma etapa lógica do processo de instalação.

## Estrutura e Propósito

A instalação é dividida em múltiplos scripts Bash, cada um nomeado com um prefixo numérico de dois dígitos para indicar a ordem de execução (ex: `01_validar_ambiente.sh`, `02_instalar_dependencias.sh`, etc.). Esta abordagem modular permite:

*   **Clareza**: Cada script foca em uma única responsabilidade.
*   **Rastreabilidade**: Logs detalhados em cada script (`[ETAPA NN] Mensagem...`) facilitam o acompanhamento e a depuração.
*   **Controle**: A execução pode ser interrompida e retomada, e cada etapa valida a conclusão da anterior.
*   **Reutilização**: Scripts individuais podem ser adaptados ou reutilizados em outros contextos.

## Scripts de Instalação

A seguir, a lista dos scripts e seus respectivos propósitos:

1.  **`01_validar_ambiente.sh`**
    *   **Propósito**: Realiza verificações prévias no sistema para garantir compatibilidade e pré-requisitos mínimos (SO, arquitetura, espaço em disco, conectividade básica, permissões).

2.  **`02_instalar_dependencias.sh`**
    *   **Propósito**: Instala todos os pacotes de software e bibliotecas dos quais a aplicação principal depende. Detecta o gerenciador de pacotes (apt, yum, dnf) e o utiliza.

3.  **`03_configurar_usuarios_grupos.sh`**
    *   **Propósito**: Cria um usuário e um grupo dedicados para a aplicação (`meuappuser`, `meuappgroup`), se não existirem, para fins de segurança e isolamento.

4.  **`04_criar_diretorios.sh`**
    *   **Propósito**: Prepara a estrutura de diretórios necessária para a instalação e operação da aplicação (ex: `/opt/meuapp`, `/etc/meuapp`, `/var/log/meuapp`), definindo permissões e propriedade adequadas.

5.  **`05_baixar_artefatos_aplicacao.sh`**
    *   **Propósito**: Baixa os binários, pacotes ou código-fonte da aplicação de uma URL especificada, verifica sua integridade (checksum MD5/SHA256) e extrai o conteúdo se for um arquivo compactado (tar.gz, zip).

6.  **`06_configurar_aplicacao.sh`**
    *   **Propósito**: Configura a aplicação, copiando arquivos de configuração template, substituindo placeholders (simulado no exemplo, requer adaptação) e realizando outras tarefas de configuração específicas.

7.  **`07_inicializar_servicos.sh`**
    *   **Propósito**: Configura e inicia os serviços ou daemons da aplicação, com foco em systemd. Inclui copiar o arquivo de unit, recarregar o daemon, habilitar e iniciar o serviço.

8.  **`08_validacao_pos_instalacao.sh`**
    *   **Propósito**: Realiza verificações básicas para confirmar que a aplicação foi instalada corretamente e está funcional (ex: checar status do serviço, testar endpoint de health check, verificar logs por erros).

9.  **`09_limpeza_instalacao.sh`**
    *   **Propósito**: Remove arquivos temporários de instalação que não são mais necessários (ex: artefato baixado, diretórios temporários de instalação).

10. **`10_iniciar_frontend.sh`**
    *   **Propósito**: Inicia o servidor web (Flask) que hospeda o painel de controle frontend do sistema Autocura. Este script deve ser executado após todas as outras etapas de instalação e configuração terem sido concluídas com sucesso. Ele torna a interface do usuário acessível via navegador.

## Fluxo de Execução e Controle

*   **Ordem Numérica**: Os scripts devem ser executados na ordem indicada por seus prefixos numéricos (de `01` a `09`).
*   **Arquivos de Flag**: Cada script, ao ser concluído com sucesso, cria um arquivo de "flag" no diretório `/tmp` (ex: `.etapa_01_ok`, `.etapa_02_ok`, etc.).
*   **Validação de Etapa Anterior**: Antes de iniciar sua execução principal, cada script (a partir do `02`) verifica a existência do arquivo de flag da etapa anterior. Se o flag não for encontrado, o script é interrompido com uma mensagem de erro, garantindo que as etapas sejam executadas na sequência correta e que uma etapa só comece após o sucesso da anterior.
*   **Tratamento de Erros**: Todos os scripts utilizam `set -e`, o que faz com que o script seja interrompido imediatamente se qualquer comando falhar. Mensagens de erro claras são exibidas, e os scripts saem com `exit 1` em caso de falha.

## Instruções de Uso

1.  **Tornar Scripts Executáveis**:
    Antes de executar, conceda permissão de execução a todos os scripts:
    ```bash
    chmod +x *.sh
    ```
    Ou individualmente:
    ```bash
    chmod +x 01_validar_ambiente.sh
    chmod +x 02_instalar_dependencias.sh
    # ... e assim por diante para todos os scripts.
    ```

2.  **Execução Sequencial**:
    Execute os scripts um por um, na ordem numérica:
    ```bash
    sudo ./01_validar_ambiente.sh
    sudo ./02_instalar_dependencias.sh
    sudo ./03_configurar_usuarios_grupos.sh
    sudo ./04_criar_diretorios.sh
    sudo ./05_baixar_artefatos_aplicacao.sh
    sudo ./06_configurar_aplicacao.sh
    sudo ./07_inicializar_servicos.sh
    sudo ./08_validacao_pos_instalacao.sh
    sudo ./09_limpeza_instalacao.sh
    sudo ./10_iniciar_frontend.sh
    ```
    **Nota sobre `sudo`**: Muitos scripts contêm comandos que requerem privilégios de superusuário (ex: instalar pacotes, criar usuários, modificar diretórios do sistema). Portanto, é provável que você precise executá-los com `sudo`.

3.  **Script Orquestrador (Opcional)**:
    Para automatizar a execução sequencial, você pode criar um script orquestrador simples (ex: `install_all.sh`):
    ```bash
    #!/bin/bash
    set -e
    echo "Iniciando processo de instalação modularizada..."
    SCRIPTS_DIR="$(pwd)" # Ou o diretório onde os scripts estão

    for script_num in $(seq -f "%02g" 1 9); do
        script_file=$(ls "${SCRIPTS_DIR}"/${script_num}_*.sh | head -n 1)
        if [ -f "${script_file}" ]; then
            echo "----------------------------------------------------------------------"
            echo "Executando: ${script_file}"
            echo "----------------------------------------------------------------------"
            if sudo "${script_file}"; then
                echo "Script ${script_file} concluído com sucesso."
            else
                echo "Erro na execução do script ${script_file}. Abortando instalação." >&2
                exit 1
            fi
        else
            echo "Aviso: Script para a etapa ${script_num} não encontrado. Pulando." >&2
        fi
    done
    echo "----------------------------------------------------------------------"
    echo "Processo de instalação modularizada concluído com sucesso!"
    echo "----------------------------------------------------------------------"
    exit 0
    ```
    Lembre-se de tornar `install_all.sh` executável também (`chmod +x install_all.sh`).

## Teste de Etapas Individuais

Para testar uma etapa individualmente (após garantir que as anteriores foram concluídas e seus flags existem):

1.  **Execute o script da etapa**: `sudo ./NN_nome_da_etapa.sh`
2.  **Verifique os logs**: Observe a saída do console para mensagens `[ETAPA NN] ...`.
3.  **Confirme as ações**: Verifique se as ações específicas do script foram realizadas (ex: pacote instalado, usuário criado, diretório existe com as permissões corretas, serviço está ativo).
4.  **Verifique o flag de sucesso**: Confirme a criação do arquivo `.etapa_NN_ok` em `/tmp`.

## Recomendações Adicionais nos Scripts

*   **Cabeçalhos Descritivos**: Cada script inicia com comentários descrevendo seu propósito.
*   **Variáveis para Caminhos Críticos**: Caminhos de diretórios importantes, URLs e nomes de arquivos são definidos como variáveis no início de cada script para facilitar a customização.
*   **Logs Claros**: Mensagens de log prefixadas com `[ETAPA NN]` indicam o progresso e o resultado das operações.

Este conjunto de scripts fornece uma base robusta para um processo de instalação automatizado e gerenciável. Adapte as variáveis e os comandos específicos dentro de cada script para atender às necessidades exatas da sua aplicação.

