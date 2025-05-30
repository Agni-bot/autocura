"""
Interface para Sensores Nano
Fase Delta - Sistema AutoCura

Implementa:
- Sensores químicos em nanoescala
- Sensores biológicos
- Sensores físicos (temperatura, pressão, etc)
- Integração e fusão de dados
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Callable, Set
import numpy as np
from datetime import datetime
import asyncio
import json


class SensorType(Enum):
    """Tipos de sensores nano"""
    CHEMICAL = "chemical"
    BIOLOGICAL = "biological"
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    PH = "ph"
    ELECTRICAL = "electrical"
    OPTICAL = "optical"
    MAGNETIC = "magnetic"
    MECHANICAL = "mechanical"
    ACOUSTIC = "acoustic"


class SensorMode(Enum):
    """Modos de operação do sensor"""
    CONTINUOUS = "continuous"
    PERIODIC = "periodic"
    ON_DEMAND = "on_demand"
    TRIGGERED = "triggered"
    ADAPTIVE = "adaptive"


class SignalType(Enum):
    """Tipos de sinais detectados"""
    ANALOG = "analog"
    DIGITAL = "digital"
    QUANTUM = "quantum"
    MOLECULAR = "molecular"


@dataclass
class SensorReading:
    """Leitura individual de sensor"""
    sensor_id: str
    sensor_type: SensorType
    timestamp: datetime
    value: Any
    unit: str
    confidence: float = 1.0  # 0-1
    location: Optional[Tuple[float, float, float]] = None  # x, y, z em nm
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "type": self.sensor_type.value,
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "unit": self.unit,
            "confidence": self.confidence,
            "location": self.location,
            "metadata": self.metadata
        }


@dataclass
class CalibrationData:
    """Dados de calibração do sensor"""
    sensor_id: str
    calibration_date: datetime
    reference_values: Dict[str, float]
    correction_factors: Dict[str, float]
    drift_rate: float = 0.0  # Deriva por hora
    next_calibration: Optional[datetime] = None
    
    def is_calibration_needed(self) -> bool:
        """Verifica se precisa recalibrar"""
        if self.next_calibration:
            return datetime.now() > self.next_calibration
        return False


class NanoSensorInterface(ABC):
    """Interface abstrata para sensores nano"""
    
    def __init__(self, sensor_id: str, sensor_type: SensorType):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.mode = SensorMode.CONTINUOUS
        self.is_active = False
        self.sensitivity = 1.0  # Fator de sensibilidade
        self.noise_level = 0.01  # Nível de ruído (0-1)
        self.power_consumption = 0.1  # mW
        self.calibration: Optional[CalibrationData] = None
        self.reading_history: List[SensorReading] = []
        self.max_history = 1000
        self.simulation_mode = True
        
        # Callbacks para eventos
        self.event_callbacks: Dict[str, List[Callable]] = {
            "threshold_exceeded": [],
            "anomaly_detected": [],
            "calibration_needed": []
        }
        
        # Configurações específicas por tipo
        self._configure_sensor_specifics()
    
    @abstractmethod
    async def read(self) -> SensorReading:
        """Realiza leitura do sensor"""
        pass
    
    @abstractmethod
    async def calibrate(self, reference_values: Dict[str, float]) -> bool:
        """Calibra o sensor com valores de referência"""
        pass
    
    @abstractmethod
    def get_specifications(self) -> Dict[str, Any]:
        """Retorna especificações técnicas do sensor"""
        pass
    
    async def activate(self) -> bool:
        """Ativa o sensor"""
        self.is_active = True
        return True
    
    async def deactivate(self) -> bool:
        """Desativa o sensor"""
        self.is_active = False
        return True
    
    def set_mode(self, mode: SensorMode, **kwargs) -> bool:
        """Define modo de operação"""
        self.mode = mode
        
        if mode == SensorMode.PERIODIC:
            self.period = kwargs.get("period", 1.0)  # segundos
        elif mode == SensorMode.TRIGGERED:
            self.trigger_condition = kwargs.get("condition", lambda x: False)
        elif mode == SensorMode.ADAPTIVE:
            self.adaptation_function = kwargs.get("adaptation_fn", lambda x: x)
        
        return True
    
    def add_reading_to_history(self, reading: SensorReading):
        """Adiciona leitura ao histórico"""
        self.reading_history.append(reading)
        
        # Mantém tamanho máximo
        if len(self.reading_history) > self.max_history:
            self.reading_history.pop(0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calcula estatísticas das leituras"""
        if not self.reading_history:
            return {}
        
        values = [r.value for r in self.reading_history if isinstance(r.value, (int, float))]
        
        if not values:
            return {}
        
        return {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "median": np.median(values),
            "count": len(values),
            "last_reading": self.reading_history[-1].to_dict() if self.reading_history else None
        }
    
    def detect_anomalies(self, method: str = "zscore", threshold: float = 3.0) -> List[SensorReading]:
        """Detecta anomalias nas leituras"""
        if len(self.reading_history) < 10:
            return []
        
        values = [r.value for r in self.reading_history if isinstance(r.value, (int, float))]
        
        if method == "zscore":
            mean = np.mean(values)
            std = np.std(values)
            
            anomalies = []
            for i, reading in enumerate(self.reading_history):
                if isinstance(reading.value, (int, float)):
                    z_score = abs((reading.value - mean) / std) if std > 0 else 0
                    if z_score > threshold:
                        anomalies.append(reading)
                        self._trigger_event("anomaly_detected", {
                            "reading": reading.to_dict(),
                            "z_score": z_score
                        })
            
            return anomalies
        
        return []
    
    def _configure_sensor_specifics(self):
        """Configura parâmetros específicos por tipo de sensor"""
        if self.sensor_type == SensorType.CHEMICAL:
            self.detection_limit = 1e-9  # mol/L
            self.response_time = 0.1  # segundos
            self.selectivity = 0.95
            
        elif self.sensor_type == SensorType.BIOLOGICAL:
            self.detection_limit = 1e-12  # mol/L
            self.response_time = 1.0
            self.specificity = 0.99
            
        elif self.sensor_type == SensorType.TEMPERATURE:
            self.range = (-50, 150)  # Celsius
            self.resolution = 0.01
            self.accuracy = 0.1
            
        elif self.sensor_type == SensorType.PRESSURE:
            self.range = (0, 1000)  # kPa
            self.resolution = 0.1
            self.accuracy = 1.0
            
        elif self.sensor_type == SensorType.PH:
            self.range = (0, 14)
            self.resolution = 0.01
            self.accuracy = 0.05
    
    def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """Dispara callbacks de evento"""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                callback(data)
    
    def register_event_callback(self, event_type: str, callback: Callable):
        """Registra callback para evento"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)


class ChemicalSensor(NanoSensorInterface):
    """Sensor químico específico"""
    
    def __init__(self, sensor_id: str, target_molecules: List[str]):
        super().__init__(sensor_id, SensorType.CHEMICAL)
        self.target_molecules = target_molecules
        self.binding_sites = 100  # Número de sítios de ligação
        self.occupied_sites = 0
        self.binding_affinity = {mol: np.random.uniform(0.8, 1.0) for mol in target_molecules}
    
    async def read(self) -> SensorReading:
        """Realiza leitura química"""
        if not self.is_active:
            raise RuntimeError("Sensor não está ativo")
        
        # Simula detecção molecular
        if self.simulation_mode:
            # Simula concentração baseada em ocupação de sítios
            concentration = self.occupied_sites / self.binding_sites * 1e-6  # mol/L
            
            # Adiciona ruído
            noise = np.random.normal(0, self.noise_level * concentration)
            measured_value = max(0, concentration + noise)
            
            # Simula mudança temporal
            self.occupied_sites = int(
                self.occupied_sites * 0.95 + 
                np.random.poisson(5)
            )
            self.occupied_sites = min(self.occupied_sites, self.binding_sites)
        else:
            # Interface com hardware real
            measured_value = await self._read_hardware()
        
        reading = SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            timestamp=datetime.now(),
            value=measured_value,
            unit="mol/L",
            confidence=self._calculate_confidence(),
            metadata={
                "target_molecules": self.target_molecules,
                "occupied_sites": self.occupied_sites,
                "binding_sites": self.binding_sites
            }
        )
        
        self.add_reading_to_history(reading)
        return reading
    
    async def calibrate(self, reference_values: Dict[str, float]) -> bool:
        """Calibra sensor químico"""
        # Reseta sítios de ligação
        self.occupied_sites = 0
        
        # Calcula fatores de correção
        correction_factors = {}
        for molecule, ref_concentration in reference_values.items():
            if molecule in self.target_molecules:
                # Simula exposição à concentração de referência
                expected_sites = int(ref_concentration * self.binding_sites / 1e-6)
                measured_sites = expected_sites + np.random.randint(-5, 5)
                
                correction_factors[molecule] = expected_sites / measured_sites if measured_sites > 0 else 1.0
        
        self.calibration = CalibrationData(
            sensor_id=self.sensor_id,
            calibration_date=datetime.now(),
            reference_values=reference_values,
            correction_factors=correction_factors,
            drift_rate=0.01,  # 1% por hora
            next_calibration=datetime.now().replace(hour=datetime.now().hour + 24)
        )
        
        return True
    
    def get_specifications(self) -> Dict[str, Any]:
        """Especificações do sensor químico"""
        return {
            "type": self.sensor_type.value,
            "target_molecules": self.target_molecules,
            "detection_limit": f"{self.detection_limit} mol/L",
            "response_time": f"{self.response_time} s",
            "selectivity": self.selectivity,
            "binding_sites": self.binding_sites,
            "binding_affinity": self.binding_affinity,
            "power_consumption": f"{self.power_consumption} mW"
        }
    
    def _calculate_confidence(self) -> float:
        """Calcula confiança da medição"""
        # Baseado em ocupação de sítios e calibração
        site_confidence = min(self.occupied_sites / 10, 1.0)  # Precisa pelo menos 10 sítios
        
        calibration_confidence = 1.0
        if self.calibration and self.calibration.is_calibration_needed():
            calibration_confidence = 0.8
        
        return site_confidence * calibration_confidence * (1 - self.noise_level)
    
    async def _read_hardware(self) -> float:
        """Leitura de hardware real (placeholder)"""
        # Implementação futura para hardware real
        return 0.0


class BiologicalSensor(NanoSensorInterface):
    """Sensor biológico específico"""
    
    def __init__(self, sensor_id: str, biomarkers: List[str]):
        super().__init__(sensor_id, SensorType.BIOLOGICAL)
        self.biomarkers = biomarkers
        self.antibodies = {marker: np.random.randint(50, 150) for marker in biomarkers}
        self.bound_antigens = {marker: 0 for marker in biomarkers}
    
    async def read(self) -> SensorReading:
        """Realiza leitura biológica"""
        if not self.is_active:
            raise RuntimeError("Sensor não está ativo")
        
        # Simula detecção de biomarcadores
        if self.simulation_mode:
            detected_markers = {}
            
            for marker in self.biomarkers:
                # Simula ligação antígeno-anticorpo
                binding_probability = 0.1  # 10% por ciclo
                new_bindings = np.random.binomial(
                    self.antibodies[marker] - self.bound_antigens[marker],
                    binding_probability
                )
                
                self.bound_antigens[marker] = min(
                    self.bound_antigens[marker] + new_bindings,
                    self.antibodies[marker]
                )
                
                # Calcula concentração
                concentration = (
                    self.bound_antigens[marker] / 
                    self.antibodies[marker] * 
                    1e-9  # ng/mL
                )
                
                detected_markers[marker] = concentration
            
            measured_value = detected_markers
        else:
            measured_value = await self._read_hardware()
        
        reading = SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            timestamp=datetime.now(),
            value=measured_value,
            unit="ng/mL",
            confidence=self._calculate_confidence(),
            metadata={
                "biomarkers": self.biomarkers,
                "antibody_count": self.antibodies,
                "bound_antigens": self.bound_antigens.copy()
            }
        )
        
        self.add_reading_to_history(reading)
        return reading
    
    async def calibrate(self, reference_values: Dict[str, float]) -> bool:
        """Calibra sensor biológico"""
        # Reseta ligações
        self.bound_antigens = {marker: 0 for marker in self.biomarkers}
        
        # Regenera anticorpos
        for marker in self.biomarkers:
            self.antibodies[marker] = np.random.randint(50, 150)
        
        self.calibration = CalibrationData(
            sensor_id=self.sensor_id,
            calibration_date=datetime.now(),
            reference_values=reference_values,
            correction_factors={marker: 1.0 for marker in self.biomarkers},
            drift_rate=0.02,  # 2% por hora (maior que químico)
            next_calibration=datetime.now().replace(hour=datetime.now().hour + 12)
        )
        
        return True
    
    def get_specifications(self) -> Dict[str, Any]:
        """Especificações do sensor biológico"""
        return {
            "type": self.sensor_type.value,
            "biomarkers": self.biomarkers,
            "detection_limit": f"{self.detection_limit} mol/L",
            "response_time": f"{self.response_time} s",
            "specificity": self.specificity,
            "antibodies": self.antibodies,
            "power_consumption": f"{self.power_consumption} mW"
        }
    
    def _calculate_confidence(self) -> float:
        """Calcula confiança da medição biológica"""
        # Baseado em taxa de ligação e especificidade
        avg_binding_rate = np.mean([
            self.bound_antigens[m] / self.antibodies[m] 
            for m in self.biomarkers
        ])
        
        return avg_binding_rate * self.specificity * (1 - self.noise_level)
    
    async def _read_hardware(self) -> Dict[str, float]:
        """Leitura de hardware real (placeholder)"""
        return {marker: 0.0 for marker in self.biomarkers}


class PhysicalSensor(NanoSensorInterface):
    """Sensor físico genérico (temperatura, pressão, etc)"""
    
    def __init__(self, sensor_id: str, sensor_type: SensorType):
        super().__init__(sensor_id, sensor_type)
        self.last_value = self._get_baseline_value()
        self.drift = 0.0
    
    async def read(self) -> SensorReading:
        """Realiza leitura física"""
        if not self.is_active:
            raise RuntimeError("Sensor não está ativo")
        
        if self.simulation_mode:
            # Simula leitura com continuidade temporal
            if self.sensor_type == SensorType.TEMPERATURE:
                # Temperatura com variação lenta
                target = 37.0 + np.sin(datetime.now().timestamp() / 100) * 2
                self.last_value += (target - self.last_value) * 0.1
                noise = np.random.normal(0, 0.1)
                measured_value = self.last_value + noise
                unit = "°C"
                
            elif self.sensor_type == SensorType.PRESSURE:
                # Pressão com flutuações
                base_pressure = 101.325
                variation = np.random.normal(0, 2)
                measured_value = base_pressure + variation + self.drift
                unit = "kPa"
                
            elif self.sensor_type == SensorType.PH:
                # pH relativamente estável
                target = 7.4
                self.last_value += (target - self.last_value) * 0.05
                noise = np.random.normal(0, 0.02)
                measured_value = np.clip(self.last_value + noise, 0, 14)
                unit = "pH"
                
            else:
                measured_value = self.last_value
                unit = "units"
            
            # Adiciona deriva
            self.drift += np.random.normal(0, 0.001)
        else:
            measured_value = await self._read_hardware()
            unit = self._get_unit()
        
        reading = SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            timestamp=datetime.now(),
            value=measured_value,
            unit=unit,
            confidence=self._calculate_confidence(),
            metadata={
                "drift": self.drift,
                "range": getattr(self, 'range', None),
                "resolution": getattr(self, 'resolution', None)
            }
        )
        
        self.add_reading_to_history(reading)
        
        # Verifica limites
        if hasattr(self, 'range'):
            if measured_value < self.range[0] or measured_value > self.range[1]:
                self._trigger_event("threshold_exceeded", {
                    "reading": reading.to_dict(),
                    "range": self.range
                })
        
        return reading
    
    async def calibrate(self, reference_values: Dict[str, float]) -> bool:
        """Calibra sensor físico"""
        # Ajusta deriva baseado em referência
        if "reference" in reference_values:
            current_reading = await self.read()
            error = reference_values["reference"] - current_reading.value
            self.drift = -error  # Compensa erro
        
        self.calibration = CalibrationData(
            sensor_id=self.sensor_id,
            calibration_date=datetime.now(),
            reference_values=reference_values,
            correction_factors={"offset": self.drift},
            drift_rate=0.001,  # 0.1% por hora
            next_calibration=datetime.now().replace(day=datetime.now().day + 7)
        )
        
        return True
    
    def get_specifications(self) -> Dict[str, Any]:
        """Especificações do sensor físico"""
        specs = {
            "type": self.sensor_type.value,
            "power_consumption": f"{self.power_consumption} mW"
        }
        
        if hasattr(self, 'range'):
            specs["range"] = f"{self.range[0]} - {self.range[1]}"
        if hasattr(self, 'resolution'):
            specs["resolution"] = self.resolution
        if hasattr(self, 'accuracy'):
            specs["accuracy"] = self.accuracy
        
        return specs
    
    def _get_baseline_value(self) -> float:
        """Valor inicial baseado no tipo"""
        baselines = {
            SensorType.TEMPERATURE: 37.0,
            SensorType.PRESSURE: 101.325,
            SensorType.PH: 7.4,
            SensorType.ELECTRICAL: 0.0,
            SensorType.OPTICAL: 1.0,
            SensorType.MAGNETIC: 0.0,
            SensorType.MECHANICAL: 0.0,
            SensorType.ACOUSTIC: 0.0
        }
        return baselines.get(self.sensor_type, 0.0)
    
    def _get_unit(self) -> str:
        """Unidade baseada no tipo"""
        units = {
            SensorType.TEMPERATURE: "°C",
            SensorType.PRESSURE: "kPa",
            SensorType.PH: "pH",
            SensorType.ELECTRICAL: "mV",
            SensorType.OPTICAL: "lux",
            SensorType.MAGNETIC: "nT",
            SensorType.MECHANICAL: "pN",
            SensorType.ACOUSTIC: "dB"
        }
        return units.get(self.sensor_type, "units")
    
    def _calculate_confidence(self) -> float:
        """Calcula confiança da medição física"""
        # Baseado em calibração e deriva
        base_confidence = 0.95
        
        if self.calibration and self.calibration.is_calibration_needed():
            base_confidence *= 0.9
        
        # Penaliza por deriva excessiva
        drift_penalty = min(abs(self.drift) / 10, 0.2)
        
        return base_confidence - drift_penalty
    
    async def _read_hardware(self) -> float:
        """Leitura de hardware real (placeholder)"""
        return 0.0


class SensorArray:
    """Array de múltiplos sensores para fusão de dados"""
    
    def __init__(self, array_id: str):
        self.array_id = array_id
        self.sensors: Dict[str, NanoSensorInterface] = {}
        self.fusion_algorithms = {
            "average": self._fusion_average,
            "weighted": self._fusion_weighted,
            "kalman": self._fusion_kalman,
            "bayesian": self._fusion_bayesian
        }
        self.active_fusion = "weighted"
        
    def add_sensor(self, sensor: NanoSensorInterface) -> bool:
        """Adiciona sensor ao array"""
        if sensor.sensor_id not in self.sensors:
            self.sensors[sensor.sensor_id] = sensor
            return True
        return False
    
    def remove_sensor(self, sensor_id: str) -> bool:
        """Remove sensor do array"""
        if sensor_id in self.sensors:
            del self.sensors[sensor_id]
            return True
        return False
    
    async def read_all(self) -> Dict[str, SensorReading]:
        """Lê todos os sensores do array"""
        readings = {}
        
        # Leituras paralelas
        tasks = []
        for sensor_id, sensor in self.sensors.items():
            if sensor.is_active:
                task = asyncio.create_task(sensor.read())
                tasks.append((sensor_id, task))
        
        # Aguarda todas as leituras
        for sensor_id, task in tasks:
            try:
                reading = await task
                readings[sensor_id] = reading
            except Exception as e:
                print(f"Erro ao ler sensor {sensor_id}: {e}")
        
        return readings
    
    async def fused_reading(self, sensor_type: Optional[SensorType] = None) -> Dict[str, Any]:
        """Retorna leitura fundida de múltiplos sensores"""
        readings = await self.read_all()
        
        # Filtra por tipo se especificado
        if sensor_type:
            readings = {
                sid: r for sid, r in readings.items() 
                if r.sensor_type == sensor_type
            }
        
        if not readings:
            return {}
        
        # Aplica algoritmo de fusão
        fusion_fn = self.fusion_algorithms.get(self.active_fusion, self._fusion_average)
        return fusion_fn(readings)
    
    def _fusion_average(self, readings: Dict[str, SensorReading]) -> Dict[str, Any]:
        """Fusão por média simples"""
        # Agrupa por tipo de sensor
        by_type = {}
        for reading in readings.values():
            if reading.sensor_type not in by_type:
                by_type[reading.sensor_type] = []
            by_type[reading.sensor_type].append(reading)
        
        results = {}
        for sensor_type, type_readings in by_type.items():
            values = [r.value for r in type_readings if isinstance(r.value, (int, float))]
            if values:
                results[sensor_type.value] = {
                    "value": np.mean(values),
                    "std": np.std(values),
                    "confidence": np.mean([r.confidence for r in type_readings]),
                    "unit": type_readings[0].unit,
                    "sensor_count": len(type_readings)
                }
        
        return results
    
    def _fusion_weighted(self, readings: Dict[str, SensorReading]) -> Dict[str, Any]:
        """Fusão ponderada por confiança"""
        by_type = {}
        for reading in readings.values():
            if reading.sensor_type not in by_type:
                by_type[reading.sensor_type] = []
            by_type[reading.sensor_type].append(reading)
        
        results = {}
        for sensor_type, type_readings in by_type.items():
            values = []
            weights = []
            
            for r in type_readings:
                if isinstance(r.value, (int, float)):
                    values.append(r.value)
                    weights.append(r.confidence)
            
            if values and weights:
                weighted_avg = np.average(values, weights=weights)
                results[sensor_type.value] = {
                    "value": weighted_avg,
                    "confidence": np.mean(weights),
                    "unit": type_readings[0].unit,
                    "sensor_count": len(type_readings),
                    "weight_distribution": weights
                }
        
        return results
    
    def _fusion_kalman(self, readings: Dict[str, SensorReading]) -> Dict[str, Any]:
        """Fusão usando filtro de Kalman (simplificado)"""
        # Implementação simplificada de Kalman
        results = {}
        
        # Por enquanto, usa weighted como fallback
        return self._fusion_weighted(readings)
    
    def _fusion_bayesian(self, readings: Dict[str, SensorReading]) -> Dict[str, Any]:
        """Fusão bayesiana (simplificada)"""
        # Implementação simplificada bayesiana
        results = {}
        
        # Por enquanto, usa weighted como fallback
        return self._fusion_weighted(readings)
    
    def get_array_status(self) -> Dict[str, Any]:
        """Status completo do array de sensores"""
        active_sensors = sum(1 for s in self.sensors.values() if s.is_active)
        
        sensor_types = {}
        for sensor in self.sensors.values():
            sensor_type = sensor.sensor_type.value
            if sensor_type not in sensor_types:
                sensor_types[sensor_type] = 0
            sensor_types[sensor_type] += 1
        
        return {
            "array_id": self.array_id,
            "total_sensors": len(self.sensors),
            "active_sensors": active_sensors,
            "sensor_types": sensor_types,
            "fusion_algorithm": self.active_fusion,
            "sensors": {
                sid: {
                    "type": s.sensor_type.value,
                    "active": s.is_active,
                    "mode": s.mode.value,
                    "statistics": s.get_statistics()
                }
                for sid, s in self.sensors.items()
            }
        }
    
    async def calibrate_all(self, reference_values: Dict[str, Dict[str, float]]) -> Dict[str, bool]:
        """Calibra todos os sensores do array"""
        results = {}
        
        for sensor_id, sensor in self.sensors.items():
            try:
                # Usa valores de referência específicos ou genéricos
                ref_values = reference_values.get(
                    sensor_id, 
                    reference_values.get("default", {})
                )
                
                success = await sensor.calibrate(ref_values)
                results[sensor_id] = success
            except Exception as e:
                print(f"Erro ao calibrar sensor {sensor_id}: {e}")
                results[sensor_id] = False
        
        return results
    
    def detect_sensor_failures(self) -> List[str]:
        """Detecta sensores com falha"""
        failed_sensors = []
        
        for sensor_id, sensor in self.sensors.items():
            # Verifica se sensor está respondendo
            if not sensor.is_active:
                continue
            
            # Verifica histórico recente
            if sensor.reading_history:
                recent_readings = sensor.reading_history[-10:]
                
                # Detecta leituras constantes (sensor travado)
                if len(set(r.value for r in recent_readings)) == 1:
                    failed_sensors.append(sensor_id)
                
                # Detecta ruído excessivo
                values = [r.value for r in recent_readings if isinstance(r.value, (int, float))]
                if values and np.std(values) > np.mean(values) * 0.5:
                    failed_sensors.append(sensor_id)
        
        return list(set(failed_sensors))


class NanoSensorProtocol:
    """Protocolo para implementações específicas de sensores"""
    
    def connect_to_hardware(self) -> bool:
        """Conecta ao hardware do sensor"""
        ...
    
    def perform_self_test(self) -> Dict[str, Any]:
        """Executa autoteste do sensor"""
        ...
    
    def get_raw_data(self) -> Any:
        """Obtém dados brutos do sensor"""
        ...
    
    def apply_compensation(self, raw_value: float) -> float:
        """Aplica compensação aos dados brutos"""
        ... 