from setuptools import setup, find_packages

setup(
    name="autocura",
    version="0.1.0",
    description="Sistema de Autocura com IA",
    author="Equipe Autocura",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "pandas>=1.3.0",
        "psutil>=5.8.0",
        "python-telegram-bot>=13.7",
        "slack-sdk>=3.11.0",
        "schedule>=1.1.0",
        "pytz>=2021.1",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0",
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
        "pytest>=7.0.0",
        "pytest-cov>=3.0.0",
        "black>=22.0.0",
        "flake8>=4.0.0",
        "mypy>=0.910",
        "isort>=5.10.0",
        "prometheus-client>=0.14.0",
        "grafana-api-client>=1.0.0",
        "kubernetes>=26.0.0",
        "docker>=6.0.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "pydantic>=2.0.0",
        "loguru>=0.7.0",
        "tenacity>=8.0.0",
        "cryptography>=41.0.0",
        "python-jose>=3.3.0",
        "passlib>=1.7.4",
        "bcrypt>=4.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
            "isort>=5.10.0",
            "pre-commit>=3.0.0",
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0"
        ],
        "monitoring": [
            "prometheus-client>=0.14.0",
            "grafana-api-client>=1.0.0",
            "opentelemetry-api>=1.0.0",
            "opentelemetry-sdk>=1.0.0"
        ],
        "security": [
            "cryptography>=41.0.0",
            "python-jose>=3.3.0",
            "passlib>=1.7.4",
            "bcrypt>=4.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "autocura=main:main",
            "autocura-monitor=monitoramento.main:main",
            "autocura-diagnostico=diagnostico.main:main"
        ]
    }
) 