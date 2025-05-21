from setuptools import setup, find_packages

setup(
    name="autocura",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.2",
        "numpy>=1.26.4",
        "pandas>=1.3.0",
        "torch>=2.1.1",
        "langchain>=0.1.0",
        "langchain-groq>=0.1.0",
        "langgraph>=0.0.15",
        "groq>=0.4.2",
    ],
    python_requires=">=3.8",
    author="Equipe de Desenvolvimento",
    description="Sistema de Autocura Cognitiva",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
) 