from setuptools import setup, find_packages

setup(
    name="autocura",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "redis>=4.0.0",
        "prometheus-client>=0.11.0",
        "python-json-logger>=2.0.0",
        "pytest>=6.0.0",
        "pytest-asyncio>=0.15.0",
        "pytest-cov>=2.12.0",
    ],
    extras_require={
        "dev": [
            "black>=21.0.0",
            "isort>=5.9.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "test": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.15.0",
            "pytest-cov>=2.12.0",
        ],
    },
    python_requires=">=3.10",
    author="AutoCura Team",
    author_email="team@autocura.com",
    description="Sistema de autocura e monitoramento inteligente",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/autocura",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
) 