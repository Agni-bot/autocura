"""
Módulo Nano - Sistema AutoCura
Fase Delta: Interfaces para Nanotecnologia

Este módulo implementa:
- Interfaces para controle de nanobots
- Simulação de sistemas moleculares
- Assembly molecular programável
- Integração com sensores nano
"""

from .src.interfaces.nanobot_interface import NanobotInterface, NanobotSwarm
from .src.interfaces.molecular_interface import MolecularAssemblyInterface
from .src.simulation.nano_simulator import NanoSimulator
from .src.sensors.nano_sensor_interface import NanoSensorInterface

__version__ = "1.0.0-delta"
__all__ = [
    "NanobotInterface",
    "NanobotSwarm",
    "MolecularAssemblyInterface",
    "NanoSimulator",
    "NanoSensorInterface"
] 