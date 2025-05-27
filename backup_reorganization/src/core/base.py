"""
Módulo base do sistema de autocura.
Contém as classes e interfaces base utilizadas por outros módulos.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseComponent(ABC):
    """Classe base para todos os componentes do sistema."""
    
    def __init__(self, name: str):
        self.name = name
        self._config: Dict[str, Any] = {}
    
    @abstractmethod
    def initialize(self) -> None:
        """Inicializa o componente."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Desliga o componente de forma segura."""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """Retorna a configuração do componente."""
        return self._config
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """Define a configuração do componente."""
        self._config = config

class BaseService(BaseComponent):
    """Classe base para serviços do sistema."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._is_running = False
    
    @abstractmethod
    def start(self) -> None:
        """Inicia o serviço."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Para o serviço."""
        pass
    
    def is_running(self) -> bool:
        """Verifica se o serviço está em execução."""
        return self._is_running

class BaseModel(BaseComponent):
    """Classe base para modelos do sistema."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._version = "0.1.0"
    
    @abstractmethod
    def predict(self, data: Any) -> Any:
        """Realiza uma predição com o modelo."""
        pass
    
    @abstractmethod
    def train(self, data: Any) -> None:
        """Treina o modelo com os dados fornecidos."""
        pass
    
    def get_version(self) -> str:
        """Retorna a versão do modelo."""
        return self._version

class BaseValidator(BaseComponent):
    """Classe base para validadores do sistema."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._errors: List[str] = []
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Valida os dados fornecidos."""
        pass
    
    def get_errors(self) -> List[str]:
        """Retorna a lista de erros encontrados."""
        return self._errors
    
    def clear_errors(self) -> None:
        """Limpa a lista de erros."""
        self._errors = [] 