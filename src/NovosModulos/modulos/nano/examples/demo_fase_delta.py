"""
Demonstração da Fase Delta - Nanotecnologia
Sistema AutoCura

Este exemplo demonstra:
- Criação e controle de nanobots
- Montagem molecular
- Simulação física
- Sensores nano integrados
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Importa componentes da Fase Delta
from ..src.interfaces.nanobot_interface import (
    NanobotInterface, NanobotType, NanobotState,
    NanoPosition, NanoCommand, NanobotSwarm
)
from ..src.interfaces.molecular_interface import (
    MolecularAssemblyInterface, MolecularStructure,
    Atom, Bond, AtomType, BondType, MoleculeType
)
from ..src.simulation.nano_simulator import (
    NanoSimulator, SimulatedNanobot, SimulationParameters
)
from ..src.sensors.nano_sensor_interface import (
    ChemicalSensor, BiologicalSensor, PhysicalSensor,
    SensorArray, SensorType, SensorMode
)


class DemoMolecularAssembly(MolecularAssemblyInterface):
    """Implementação de demonstração de montagem molecular"""
    
    async def design_structure(self, specification: Dict[str, Any]) -> MolecularStructure:
        """Projeta estrutura baseada em especificação"""
        structure_type = specification.get("type", "drug")
        
        if structure_type == "drug":
            # Cria molécula de droga simples (aspirina-like)
            structure = MolecularStructure(
                structure_id="drug_001",
                name="Demo Drug Molecule",
                molecule_type=MoleculeType.DRUG
            )
            
            # Adiciona átomos
            c1 = Atom("C1", AtomType.CARBON, (0.0, 0.0, 0.0))
            c2 = Atom("C2", AtomType.CARBON, (1.5, 0.0, 0.0))
            o1 = Atom("O1", AtomType.OXYGEN, (0.0, 1.5, 0.0))
            h1 = Atom("H1", AtomType.HYDROGEN, (-1.0, 0.0, 0.0))
            
            for atom in [c1, c2, o1, h1]:
                structure.add_atom(atom)
            
            # Adiciona ligações
            structure.add_bond(Bond("B1", "C1", "C2", BondType.SINGLE))
            structure.add_bond(Bond("B2", "C1", "O1", BondType.DOUBLE))
            structure.add_bond(Bond("B3", "C1", "H1", BondType.SINGLE))
            
        elif structure_type == "nanostructure":
            # Cria nanoestrutura de carbono
            structure = MolecularStructure(
                structure_id="nano_001",
                name="Carbon Nanostructure",
                molecule_type=MoleculeType.NANOSTRUCTURE
            )
            
            # Cria anel hexagonal
            for i in range(6):
                angle = i * 60 * 3.14159 / 180
                x = 1.4 * np.cos(angle)
                y = 1.4 * np.sin(angle)
                atom = Atom(f"C{i+1}", AtomType.CARBON, (x, y, 0.0))
                structure.add_atom(atom)
            
            # Liga átomos em anel
            for i in range(6):
                bond = Bond(
                    f"B{i+1}",
                    f"C{i+1}",
                    f"C{(i+1)%6 + 1}",
                    BondType.AROMATIC
                )
                structure.add_bond(bond)
        
        self.current_structure = structure
        self._record_history("structure_designed", specification)
        return structure
    
    async def add_atom(self, atom_type: AtomType, position: Tuple[float, float, float]) -> str:
        """Adiciona átomo à estrutura"""
        if not self.current_structure:
            raise RuntimeError("Nenhuma estrutura ativa")
        
        atom_id = f"{atom_type.symbol}{len(self.current_structure.atoms) + 1}"
        atom = Atom(atom_id, atom_type, position)
        
        if self.current_structure.add_atom(atom):
            self._record_history("atom_added", {
                "atom_id": atom_id,
                "type": atom_type.symbol,
                "position": position
            })
            return atom_id
        
        return ""
    
    async def create_bond(self, atom1_id: str, atom2_id: str, bond_type: BondType) -> bool:
        """Cria ligação entre átomos"""
        if not self.current_structure:
            return False
        
        bond_id = f"B{len(self.current_structure.bonds) + 1}"
        bond = Bond(bond_id, atom1_id, atom2_id, bond_type)
        
        success = self.current_structure.add_bond(bond)
        if success:
            self._record_history("bond_created", {
                "bond_id": bond_id,
                "atoms": [atom1_id, atom2_id],
                "type": bond_type.value
            })
        
        return success
    
    async def remove_atom(self, atom_id: str) -> bool:
        """Remove átomo da estrutura"""
        if not self.current_structure or atom_id not in self.current_structure.atoms:
            return False
        
        # Remove ligações associadas
        bonds_to_remove = []
        for bond_id, bond in self.current_structure.bonds.items():
            if bond.atom1_id == atom_id or bond.atom2_id == atom_id:
                bonds_to_remove.append(bond_id)
        
        for bond_id in bonds_to_remove:
            del self.current_structure.bonds[bond_id]
        
        # Remove átomo
        del self.current_structure.atoms[atom_id]
        
        self._record_history("atom_removed", {"atom_id": atom_id})
        return True
    
    async def optimize_geometry(self, method: str = "MM") -> Dict[str, Any]:
        """Otimiza geometria (simulado)"""
        if not self.current_structure:
            return {"error": "Nenhuma estrutura ativa"}
        
        # Simulação simples de otimização
        initial_energy = np.random.uniform(100, 200)  # kJ/mol
        
        # "Otimiza" movendo átomos ligeiramente
        for atom in self.current_structure.atoms.values():
            # Pequeno deslocamento aleatório
            dx = np.random.normal(0, 0.01)
            dy = np.random.normal(0, 0.01)
            dz = np.random.normal(0, 0.01)
            
            new_pos = (
                atom.position[0] + dx,
                atom.position[1] + dy,
                atom.position[2] + dz
            )
            atom.position = new_pos
        
        final_energy = initial_energy * 0.8  # 20% menor
        
        result = {
            "method": method,
            "initial_energy": initial_energy,
            "final_energy": final_energy,
            "convergence": True,
            "iterations": np.random.randint(50, 200)
        }
        
        self._record_history("geometry_optimized", result)
        return result
    
    async def validate_structure(self) -> Dict[str, Any]:
        """Valida estrutura molecular"""
        if not self.current_structure:
            return {"valid": False, "error": "Nenhuma estrutura ativa"}
        
        issues = []
        
        # Verifica conectividade
        isolated_atoms = []
        for atom_id, atom in self.current_structure.atoms.items():
            if not atom.bonds:
                isolated_atoms.append(atom_id)
        
        if isolated_atoms:
            issues.append(f"Átomos isolados: {isolated_atoms}")
        
        # Verifica valência (simplificado)
        valence_map = {
            "H": 1, "C": 4, "N": 3, "O": 2,
            "P": 5, "S": 6, "Si": 4
        }
        
        for atom_id, atom in self.current_structure.atoms.items():
            expected_valence = valence_map.get(atom.atom_type.symbol, 4)
            actual_bonds = len(atom.bonds)
            
            if actual_bonds > expected_valence:
                issues.append(f"Átomo {atom_id} com valência excessiva")
        
        valid = len(issues) == 0
        
        result = {
            "valid": valid,
            "issues": issues,
            "atom_count": len(self.current_structure.atoms),
            "bond_count": len(self.current_structure.bonds),
            "molecular_formula": self.current_structure.get_molecular_formula()
        }
        
        self._record_history("structure_validated", result)
        return result
    
    async def synthesize(self, method: str = "stepwise") -> Dict[str, Any]:
        """Sintetiza molécula (simulado)"""
        if not self.current_structure:
            return {"error": "Nenhuma estrutura ativa"}
        
        validation = await self.validate_structure()
        if not validation["valid"]:
            return {
                "success": False,
                "error": "Estrutura inválida",
                "issues": validation["issues"]
            }
        
        # Simula síntese
        steps = []
        
        if method == "stepwise":
            # Síntese passo a passo
            for i, (atom_id, atom) in enumerate(self.current_structure.atoms.items()):
                steps.append({
                    "step": i + 1,
                    "action": f"Adicionar {atom.atom_type.symbol}",
                    "success": True,
                    "yield": 95 + np.random.uniform(-5, 5)
                })
        
        elif method == "convergent":
            # Síntese convergente
            steps.append({
                "step": 1,
                "action": "Preparar fragmentos",
                "success": True,
                "yield": 90
            })
            steps.append({
                "step": 2,
                "action": "Acoplar fragmentos",
                "success": True,
                "yield": 85
            })
        
        total_yield = np.prod([s["yield"]/100 for s in steps]) * 100
        
        result = {
            "success": True,
            "method": method,
            "steps": steps,
            "total_yield": total_yield,
            "purity": 95 + np.random.uniform(0, 4),
            "time_hours": len(steps) * 2
        }
        
        self._record_history("synthesis_completed", result)
        return result


async def demo_nanobot_swarm():
    """Demonstra controle de swarm de nanobots"""
    print("\n=== DEMO: Swarm de Nanobots ===\n")
    
    # Cria swarm
    swarm = NanobotSwarm("swarm_medical_001")
    
    # Adiciona diferentes tipos de nanobots
    bot_types = [
        (NanobotType.MEDICAL, 5),
        (NanobotType.SENSOR, 10),
        (NanobotType.REPAIR, 3),
        (NanobotType.COMMUNICATION, 2)
    ]
    
    for bot_type, count in bot_types:
        for i in range(count):
            bot = SimulatedNanobot(
                f"{bot_type.value}_{i+1}",
                bot_type
            )
            swarm.add_nanobot(bot)
    
    print(f"Swarm criado com {len(swarm.nanobots)} nanobots")
    
    # Forma estrutura esférica
    center = NanoPosition(500, 500, 500)
    success = await swarm.form_structure("sphere", center)
    print(f"Formação esférica: {'Sucesso' if success else 'Falha'}")
    
    # Executa comando no swarm
    command = NanoCommand(
        command_id="cmd_001",
        action="sense",
        parameters={"target": "environment"}
    )
    
    result = await swarm.execute_swarm_command(command)
    print(f"Taxa de sucesso do comando: {result['success_rate']*100:.1f}%")
    
    # Decisão coletiva
    options = [
        {"action": "move_to_target", "risk": 0.2},
        {"action": "wait_and_observe", "risk": 0.1},
        {"action": "retreat", "risk": 0.05}
    ]
    
    decision = await swarm.collective_decision(options)
    print(f"Decisão coletiva: {decision['decision']['action'] if decision['consensus'] else 'Sem consenso'}")
    
    # Status do swarm
    status = swarm.get_swarm_status()
    print(f"\nStatus do Swarm:")
    print(f"- Nanobots operacionais: {status['operational']}/{status['total_nanobots']}")
    print(f"- Energia média: {status['average_energy']:.1f}%")
    print(f"- Integridade de comunicação: {status['communication_integrity']*100:.1f}%")
    
    return swarm


async def demo_molecular_assembly():
    """Demonstra montagem molecular"""
    print("\n=== DEMO: Montagem Molecular ===\n")
    
    assembler = DemoMolecularAssembly("assembler_001")
    
    # Projeta molécula de droga
    spec = {
        "type": "drug",
        "target": "anti-inflammatory"
    }
    
    structure = await assembler.design_structure(spec)
    print(f"Estrutura projetada: {structure.name}")
    print(f"Fórmula molecular: {structure.get_molecular_formula()}")
    print(f"Peso molecular: {structure.calculate_molecular_weight():.2f} g/mol")
    
    # Adiciona mais átomos
    n_pos = (0.0, -1.5, 0.0)
    n_id = await assembler.add_atom(AtomType.NITROGEN, n_pos)
    print(f"Átomo de nitrogênio adicionado: {n_id}")
    
    # Cria ligação
    success = await assembler.create_bond("C1", n_id, BondType.SINGLE)
    print(f"Ligação C-N criada: {'Sucesso' if success else 'Falha'}")
    
    # Otimiza geometria
    opt_result = await assembler.optimize_geometry("MM")
    print(f"Otimização: Energia {opt_result['initial_energy']:.1f} → {opt_result['final_energy']:.1f} kJ/mol")
    
    # Valida estrutura
    validation = await assembler.validate_structure()
    print(f"Estrutura válida: {'Sim' if validation['valid'] else 'Não'}")
    if not validation['valid']:
        print(f"Problemas: {validation['issues']}")
    
    # Sintetiza
    synthesis = await assembler.synthesize("stepwise")
    if synthesis['success']:
        print(f"Síntese completa!")
        print(f"- Rendimento total: {synthesis['total_yield']:.1f}%")
        print(f"- Pureza: {synthesis['purity']:.1f}%")
        print(f"- Tempo: {synthesis['time_hours']} horas")
    
    # Salva estrutura
    json_structure = await assembler.save_structure("json")
    print(f"\nEstrutura salva ({len(json_structure)} caracteres)")
    
    return assembler


async def demo_nano_simulation():
    """Demonstra simulação física de nanobots"""
    print("\n=== DEMO: Simulação Nano ===\n")
    
    # Configura parâmetros
    params = SimulationParameters(
        time_step=1e-12,  # 1 picosegundo
        temperature=310.15,  # 37°C
        box_size=(2000, 2000, 2000),  # 2 micrômetros cúbicos
        brownian_motion=True,
        electrostatic_interactions=True,
        collision_detection=True
    )
    
    simulator = NanoSimulator(params)
    
    # Adiciona nanobots
    for i in range(10):
        bot = SimulatedNanobot(
            f"sim_bot_{i+1}",
            NanobotType.SENSOR if i < 5 else NanobotType.MEDICAL
        )
        simulator.add_nanobot(bot)
    
    print(f"Simulador configurado com {len(simulator.nanobots)} nanobots")
    print(f"Volume de simulação: {params.box_size[0]}×{params.box_size[1]}×{params.box_size[2]} nm³")
    
    # Registra callbacks para eventos
    collision_count = [0]
    
    def on_collision(data):
        collision_count[0] += 1
    
    simulator.register_event_callback("collision", on_collision)
    
    # Executa simulação por 1 nanosegundo
    duration = 1e-9  # 1 ns
    print(f"\nExecutando simulação por {duration*1e9:.0f} ns...")
    
    await simulator.run_simulation(duration)
    
    # Relatório
    report = simulator.get_simulation_report()
    stats = report["final_statistics"]
    
    print(f"\nResultados da Simulação:")
    print(f"- Tempo simulado: {report['duration']*1e9:.3f} ns")
    print(f"- Passos de tempo: {report['time_steps']}")
    print(f"- Velocidade média: {stats['avg_velocity']:.1f} nm/s")
    print(f"- Temperatura cinética: {stats['kinetic_temperature']:.1f} K")
    print(f"- Colisões detectadas: {collision_count[0]}")
    print(f"- Nanobots operacionais: {stats['operational_bots']}")
    
    # Exporta visualização
    simulator.export_visualization("nano_simulation.json")
    print("\nDados de visualização exportados para 'nano_simulation.json'")
    
    return simulator


async def demo_sensor_array():
    """Demonstra array de sensores nano"""
    print("\n=== DEMO: Array de Sensores ===\n")
    
    # Cria array
    array = SensorArray("sensor_array_001")
    
    # Adiciona sensores químicos
    molecules = ["glucose", "insulin", "cortisol"]
    for i, molecule in enumerate(molecules):
        sensor = ChemicalSensor(f"chem_{i+1}", [molecule])
        await sensor.activate()
        array.add_sensor(sensor)
    
    # Adiciona sensores biológicos
    biomarkers = ["TNF-alpha", "IL-6", "CRP"]
    bio_sensor = BiologicalSensor("bio_1", biomarkers)
    await bio_sensor.activate()
    array.add_sensor(bio_sensor)
    
    # Adiciona sensores físicos
    for sensor_type in [SensorType.TEMPERATURE, SensorType.PH, SensorType.PRESSURE]:
        phys_sensor = PhysicalSensor(f"phys_{sensor_type.value}", sensor_type)
        await phys_sensor.activate()
        array.add_sensor(phys_sensor)
    
    print(f"Array configurado com {len(array.sensors)} sensores")
    
    # Leitura de todos os sensores
    readings = await array.read_all()
    print(f"\nLeituras obtidas de {len(readings)} sensores:")
    
    for sensor_id, reading in readings.items():
        print(f"- {sensor_id}: {reading.value:.3f} {reading.unit} (confiança: {reading.confidence:.2f})")
    
    # Fusão de dados
    fused = await array.fused_reading()
    print(f"\nDados fundidos (algoritmo: {array.active_fusion}):")
    for sensor_type, data in fused.items():
        print(f"- {sensor_type}: {data['value']:.3f} {data['unit']} (±{data.get('std', 0):.3f})")
    
    # Calibração
    ref_values = {
        "default": {"reference": 7.4},  # pH
        "chem_1": {"glucose": 5.0e-3},  # mmol/L
    }
    
    calib_results = await array.calibrate_all(ref_values)
    success_count = sum(1 for s in calib_results.values() if s)
    print(f"\nCalibração: {success_count}/{len(calib_results)} sensores calibrados com sucesso")
    
    # Detecção de falhas
    failed = array.detect_sensor_failures()
    if failed:
        print(f"Sensores com falha detectada: {failed}")
    else:
        print("Nenhuma falha detectada nos sensores")
    
    # Status do array
    status = array.get_array_status()
    print(f"\nStatus do Array:")
    print(f"- Sensores ativos: {status['active_sensors']}/{status['total_sensors']}")
    print(f"- Tipos de sensores: {status['sensor_types']}")
    
    return array


async def main():
    """Executa todas as demonstrações"""
    print("=" * 60)
    print("DEMONSTRAÇÃO FASE DELTA - NANOTECNOLOGIA")
    print("Sistema AutoCura")
    print("=" * 60)
    
    # Demo 1: Swarm de Nanobots
    swarm = await demo_nanobot_swarm()
    
    # Demo 2: Montagem Molecular
    assembler = await demo_molecular_assembly()
    
    # Demo 3: Simulação Física
    simulator = await demo_nano_simulation()
    
    # Demo 4: Array de Sensores
    sensor_array = await demo_sensor_array()
    
    print("\n" + "=" * 60)
    print("DEMONSTRAÇÃO CONCLUÍDA")
    print("=" * 60)
    
    # Resumo final
    print("\nResumo da Fase Delta:")
    print(f"✓ Nanobots controlados: {len(swarm.nanobots)}")
    print(f"✓ Moléculas projetadas: 1")
    print(f"✓ Simulações executadas: 1")
    print(f"✓ Sensores integrados: {len(sensor_array.sensors)}")
    print("\nSistema pronto para integração com hardware nano quando disponível!")


if __name__ == "__main__":
    # Para executar no Windows, pode ser necessário:
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main()) 