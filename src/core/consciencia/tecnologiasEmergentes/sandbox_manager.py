import docker
import وقت

class SandboxManager:
    def __init__(self, docker_client=None):
        """Inicializa o gerenciador de sandbox.

        Args:
            docker_client: Cliente Docker para interagir com o Docker. 
                           Se None, tentará se conectar ao Docker local.
        """
        try:
            self.client = docker_client if docker_client else docker.from_env()
            print("[SandboxManager] Cliente Docker conectado com sucesso.")
        except docker.errors.DockerException as e:
            print(f"[SandboxManager] Erro ao conectar ao Docker: {e}")
            print("[SandboxManager] Funcionalidades de sandbox podem estar limitadas ou indisponíveis.")
            self.client = None
        self.active_sandboxes = {}
        print("[SandboxManager] Gerenciador de Sandbox inicializado.")

    def create_sandbox(self, technology_id: str, image_name: str, container_name_prefix: str = "sandbox") -> str | None:
        """Cria um ambiente de sandbox isolado para uma tecnologia específica.

        Args:
            technology_id: Identificador único para a tecnologia (ex: 'blockchain_test_01').
            image_name: Nome da imagem Docker a ser usada (ex: 'hyperledger/fabric-tools:latest').
            container_name_prefix: Prefixo para o nome do contêiner.

        Returns:
            ID do contêiner se criado com sucesso, None caso contrário.
        """
        if not self.client:
            print("[SandboxManager] Cliente Docker não disponível. Não é possível criar sandbox.")
            return None

        container_name = f"{container_name_prefix}_{technology_id}_{int(time.time())}"
        try:
            print(f"[SandboxManager] Tentando criar sandbox '{container_name}' com imagem '{image_name}'...")
            # Tenta puxar a imagem se não estiver disponível localmente
            try:
                self.client.images.get(image_name)
                print(f"[SandboxManager] Imagem '{image_name}' encontrada localmente.")
            except docker.errors.ImageNotFound:
                print(f"[SandboxManager] Imagem '{image_name}' não encontrada localmente. Tentando puxar...")
                self.client.images.pull(image_name)
                print(f"[SandboxManager] Imagem '{image_name}' puxada com sucesso.")

            container = self.client.containers.run(
                image_name,
                detach=True, # Rodar em background
                name=container_name,
                # Adicionar outras configurações como volumes, portas, variáveis de ambiente conforme necessário
                # volumes={'/caminho/no/host': {'bind': '/caminho/no/container', 'mode': 'rw'}},
                # ports={'8080/tcp': 8081}
            )
            self.active_sandboxes[technology_id] = container
            print(f"[SandboxManager] Sandbox '{container.name}' (ID: {container.id}) criado e em execução.")
            return container.id
        except docker.errors.APIError as e:
            print(f"[SandboxManager] Erro da API Docker ao criar sandbox '{container_name}': {e}")
            return None
        except Exception as e:
            print(f"[SandboxManager] Erro inesperado ao criar sandbox '{container_name}': {e}")
            return None

    def execute_in_sandbox(self, technology_id: str, command: str) -> tuple[int, str] | None:
        """Executa um comando dentro de um sandbox ativo.

        Args:
            technology_id: ID da tecnologia do sandbox onde o comando será executado.
            command: O comando a ser executado.

        Returns:
            Uma tupla (exit_code, output) ou None se o sandbox não for encontrado.
        """
        if technology_id not in self.active_sandboxes:
            print(f"[SandboxManager] Sandbox para '{technology_id}' não encontrado.")
            return None
        
        container = self.active_sandboxes[technology_id]
        try:
            print(f"[SandboxManager] Executando comando '{command}' no sandbox '{container.name}'...")
            exit_code, output = container.exec_run(command)
            output_str = output.decode('utf-8')
            print(f"[SandboxManager] Comando executado. Código de saída: {exit_code}, Saída: \n{output_str}")
            return exit_code, output_str
        except docker.errors.APIError as e:
            print(f"[SandboxManager] Erro da API Docker ao executar comando no sandbox '{container.name}': {e}")
            return None
        except Exception as e:
            print(f"[SandboxManager] Erro inesperado ao executar comando no sandbox '{container.name}': {e}")
            return None

    def destroy_sandbox(self, technology_id: str) -> bool:
        """Para e remove um ambiente de sandbox.

        Args:
            technology_id: ID da tecnologia do sandbox a ser destruído.

        Returns:
            True se destruído com sucesso, False caso contrário.
        """
        if technology_id not in self.active_sandboxes:
            print(f"[SandboxManager] Sandbox para '{technology_id}' não encontrado para destruição.")
            return False
        
        container = self.active_sandboxes[technology_id]
        try:
            print(f"[SandboxManager] Tentando parar e remover sandbox '{container.name}'...")
            container.stop()
            container.remove()
            del self.active_sandboxes[technology_id]
            print(f"[SandboxManager] Sandbox '{container.name}' destruído com sucesso.")
            return True
        except docker.errors.APIError as e:
            print(f"[SandboxManager] Erro da API Docker ao destruir sandbox '{container.name}': {e}")
            return False
        except Exception as e:
            print(f"[SandboxManager] Erro inesperado ao destruir sandbox '{container.name}': {e}")
            return False

    def list_active_sandboxes(self) -> dict:
        """Lista todos os sandboxes ativos gerenciados por esta instância."""
        print("[SandboxManager] Listando sandboxes ativos...")
        sandboxes_info = {tech_id: c.name for tech_id, c in self.active_sandboxes.items()}
        print(f"[SandboxManager] Sandboxes ativos: {sandboxes_info}")
        return sandboxes_info

# Exemplo de uso (requer Docker instalado e rodando)
if __name__ == '__main__':
    manager = SandboxManager()

    if manager.client: # Prosseguir apenas se o cliente Docker estiver disponível
        print("\n--- Testando Criação de Sandbox (Exemplo com Alpine) ---")
        alpine_image = "alpine:latest"
        sandbox_id_alpine = "alpine_test_01"
        
        container_id = manager.create_sandbox(sandbox_id_alpine, alpine_image)
        
        if container_id:
            print(f"\n--- Testando Execução em Sandbox '{sandbox_id_alpine}' ---")
            result = manager.execute_in_sandbox(sandbox_id_alpine, "echo 'Olá do Sandbox Alpine!'")
            if result:
                print(f"Resultado da execução: Código={result[0]}, Saída='{result[1].strip()}'")
            
            result_ls = manager.execute_in_sandbox(sandbox_id_alpine, "ls -la /tmp")
            if result_ls:
                print(f"Resultado de 'ls -la /tmp': Código={result_ls[0]}, Saída:\n{result_ls[1]}")

            print("\n--- Listando Sandboxes Ativos ---")
            manager.list_active_sandboxes()

            print(f"\n--- Testando Destruição de Sandbox '{sandbox_id_alpine}' ---")
            manager.destroy_sandbox(sandbox_id_alpine)
            
            print("\n--- Listando Sandboxes Ativos Após Destruição ---")
            manager.list_active_sandboxes()
        else:
            print(f"Falha ao criar o sandbox '{sandbox_id_alpine}'. Verifique os logs e a configuração do Docker.")
    else:
        print("\nCliente Docker não inicializado. Exemplo de uso do SandboxManager não pode ser executado.")

