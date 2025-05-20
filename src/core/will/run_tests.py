import os
import sys
import pytest

# Adiciona o diretório atual ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Executa os testes
pytest.main(['tests/test_will_api.py', '-v']) 