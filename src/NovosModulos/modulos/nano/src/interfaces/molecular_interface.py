"""
Interface para Montagem Molecular
Fase Delta - Sistema AutoCura

Implementa:
- Design de estruturas moleculares
- Montagem atômica programável
- Síntese molecular controlada
- Validação de estruturas
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Set
import numpy as np
from datetime import datetime
import json


class AtomType(Enum):
    """Tipos de átomos suportados"""
    HYDROGEN = ("H", 1, 1.008)
    CARBON = ("C", 6, 12.011)
    NITROGEN = ("N", 7, 14.007)
    OXYGEN = ("O", 8, 15.999)
    PHOSPHORUS = ("P", 15, 30.974)
    SULFUR = ("S", 16, 32.065)
    SILICON = ("Si", 14, 28.085)
    IRON = ("Fe", 26, 55.845)
    GOLD = ("Au", 79, 196.967)
    
    def __init__(self, symbol: str, atomic_number: int, atomic_mass: float):
        self.symbol = symbol
        self.atomic_number = atomic_number
        self.atomic_mass = atomic_mass


class BondType(Enum):
    """Tipos de ligações químicas"""
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3
    AROMATIC = 1.5
    IONIC = 0
    METALLIC = -1
    HYDROGEN = 0.5
    VAN_DER_WAALS = 0.1


class MoleculeType(Enum):
    """Tipos de moléculas"""
    ORGANIC = "organic"
    INORGANIC = "inorganic"
    POLYMER = "polymer"
    PROTEIN = "protein"
    DNA = "dna"
    RNA = "rna"
    NANOSTRUCTURE = "nanostructure"
    DRUG = "drug"
    CATALYST = "catalyst"


@dataclass
class Atom:
    """Representa um átomo individual"""
    atom_id: str
    atom_type: AtomType
    position: Tuple[float, float, float]  # Coordenadas x, y, z em Angstroms
    charge: float = 0.0
    bonds: List[str] = field(default_factory=list)  # IDs dos átomos ligados
    
    def distance_to(self, other: 'Atom') -> float:
        """Calcula distância entre átomos"""
        return np.sqrt(sum((a - b)**2 for a, b in zip(self.position, other.position)))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.atom_id,
            "type": self.atom_type.symbol,
            "position": self.position,
            "charge": self.charge,
            "bonds": self.bonds
        }


@dataclass
class Bond:
    """Representa uma ligação química"""
    bond_id: str
    atom1_id: str
    atom2_id: str
    bond_type: BondType
    length: float = 0.0  # Angstroms
    energy: float = 0.0  # kJ/mol
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.bond_id,
            "atoms": [self.atom1_id, self.atom2_id],
            "type": self.bond_type.value,
            "length": self.length,
            "energy": self.energy
        }


@dataclass
class MolecularStructure:
    """Estrutura molecular completa"""
    structure_id: str
    name: str
    molecule_type: MoleculeType
    atoms: Dict[str, Atom] = field(default_factory=dict)
    bonds: Dict[str, Bond] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_atom(self, atom: Atom) -> bool:
        """Adiciona átomo à estrutura"""
        if atom.atom_id not in self.atoms:
            self.atoms[atom.atom_id] = atom
            return True
        return False
    
    def add_bond(self, bond: Bond) -> bool:
        """Adiciona ligação à estrutura"""
        if bond.bond_id not in self.bonds:
            self.bonds[bond.bond_id] = bond
            # Atualiza lista de ligações nos átomos
            if bond.atom1_id in self.atoms:
                self.atoms[bond.atom1_id].bonds.append(bond.atom2_id)
            if bond.atom2_id in self.atoms:
                self.atoms[bond.atom2_id].bonds.append(bond.atom1_id)
            return True
        return False
    
    def get_molecular_formula(self) -> str:
        """Retorna fórmula molecular"""
        atom_counts = {}
        for atom in self.atoms.values():
            symbol = atom.atom_type.symbol
            atom_counts[symbol] = atom_counts.get(symbol, 0) + 1
        
        # Ordena por convenção química (C, H, depois alfabético)
        formula_parts = []
        for symbol in ['C', 'H']:
            if symbol in atom_counts:
                count = atom_counts.pop(symbol)
                formula_parts.append(f"{symbol}{count if count > 1 else ''}")
        
        # Resto em ordem alfabética
        for symbol in sorted(atom_counts.keys()):
            count = atom_counts[symbol]
            formula_parts.append(f"{symbol}{count if count > 1 else ''}")
        
        return ''.join(formula_parts)
    
    def calculate_molecular_weight(self) -> float:
        """Calcula peso molecular"""
        return sum(atom.atom_type.atomic_mass for atom in self.atoms.values())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.structure_id,
            "name": self.name,
            "type": self.molecule_type.value,
            "formula": self.get_molecular_formula(),
            "molecular_weight": self.calculate_molecular_weight(),
            "atoms": [atom.to_dict() for atom in self.atoms.values()],
            "bonds": [bond.to_dict() for bond in self.bonds.values()],
            "properties": self.properties,
            "timestamp": self.timestamp.isoformat()
        }


class MolecularAssemblyInterface(ABC):
    """Interface abstrata para montagem molecular"""
    
    def __init__(self, assembly_id: str):
        self.assembly_id = assembly_id
        self.current_structure: Optional[MolecularStructure] = None
        self.assembly_history: List[Dict[str, Any]] = []
        self.simulation_mode = True  # Sempre inicia em simulação
        self.precision = 0.01  # Angstroms
        
    @abstractmethod
    async def design_structure(self, specification: Dict[str, Any]) -> MolecularStructure:
        """Projeta estrutura molecular baseada em especificação"""
        pass
    
    @abstractmethod
    async def add_atom(self, atom_type: AtomType, position: Tuple[float, float, float]) -> str:
        """Adiciona átomo em posição específica"""
        pass
    
    @abstractmethod
    async def create_bond(self, atom1_id: str, atom2_id: str, bond_type: BondType) -> bool:
        """Cria ligação entre átomos"""
        pass
    
    @abstractmethod
    async def remove_atom(self, atom_id: str) -> bool:
        """Remove átomo da estrutura"""
        pass
    
    @abstractmethod
    async def optimize_geometry(self, method: str = "MM") -> Dict[str, Any]:
        """Otimiza geometria molecular"""
        pass
    
    @abstractmethod
    async def validate_structure(self) -> Dict[str, Any]:
        """Valida estrutura molecular"""
        pass
    
    @abstractmethod
    async def synthesize(self, method: str = "stepwise") -> Dict[str, Any]:
        """Sintetiza molécula usando método especificado"""
        pass
    
    async def save_structure(self, format: str = "json") -> str:
        """Salva estrutura em formato especificado"""
        if not self.current_structure:
            return ""
        
        if format == "json":
            return json.dumps(self.current_structure.to_dict(), indent=2)
        elif format == "pdb":
            return self._to_pdb_format()
        elif format == "mol":
            return self._to_mol_format()
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    async def load_structure(self, data: str, format: str = "json") -> bool:
        """Carrega estrutura de formato especificado"""
        try:
            if format == "json":
                structure_dict = json.loads(data)
                self.current_structure = self._dict_to_structure(structure_dict)
            elif format == "pdb":
                self.current_structure = self._parse_pdb(data)
            elif format == "mol":
                self.current_structure = self._parse_mol(data)
            else:
                return False
            
            self._record_history("structure_loaded", {"format": format})
            return True
        except Exception as e:
            self._record_history("load_error", {"error": str(e)})
            return False
    
    def get_structure_properties(self) -> Dict[str, Any]:
        """Calcula propriedades da estrutura"""
        if not self.current_structure:
            return {}
        
        return {
            "molecular_formula": self.current_structure.get_molecular_formula(),
            "molecular_weight": self.current_structure.calculate_molecular_weight(),
            "atom_count": len(self.current_structure.atoms),
            "bond_count": len(self.current_structure.bonds),
            "center_of_mass": self._calculate_center_of_mass(),
            "radius_of_gyration": self._calculate_radius_of_gyration(),
            "dipole_moment": self._estimate_dipole_moment(),
            "surface_area": self._estimate_surface_area(),
            "volume": self._estimate_volume()
        }
    
    def _record_history(self, action: str, details: Dict[str, Any]):
        """Registra ação no histórico"""
        self.assembly_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        })
    
    def _calculate_center_of_mass(self) -> Tuple[float, float, float]:
        """Calcula centro de massa"""
        if not self.current_structure or not self.current_structure.atoms:
            return (0.0, 0.0, 0.0)
        
        total_mass = 0.0
        weighted_position = np.array([0.0, 0.0, 0.0])
        
        for atom in self.current_structure.atoms.values():
            mass = atom.atom_type.atomic_mass
            total_mass += mass
            weighted_position += mass * np.array(atom.position)
        
        if total_mass > 0:
            com = weighted_position / total_mass
            return tuple(com)
        return (0.0, 0.0, 0.0)
    
    def _calculate_radius_of_gyration(self) -> float:
        """Calcula raio de giração"""
        if not self.current_structure or len(self.current_structure.atoms) < 2:
            return 0.0
        
        com = self._calculate_center_of_mass()
        total_mass = 0.0
        sum_squared_distances = 0.0
        
        for atom in self.current_structure.atoms.values():
            mass = atom.atom_type.atomic_mass
            total_mass += mass
            distance = np.sqrt(sum((a - c)**2 for a, c in zip(atom.position, com)))
            sum_squared_distances += mass * distance**2
        
        if total_mass > 0:
            return np.sqrt(sum_squared_distances / total_mass)
        return 0.0
    
    def _estimate_dipole_moment(self) -> float:
        """Estima momento dipolar (simplificado)"""
        if not self.current_structure:
            return 0.0
        
        dipole = np.array([0.0, 0.0, 0.0])
        
        for atom in self.current_structure.atoms.values():
            charge = atom.charge
            position = np.array(atom.position)
            dipole += charge * position
        
        return np.linalg.norm(dipole)
    
    def _estimate_surface_area(self) -> float:
        """Estima área de superfície (método simplificado)"""
        if not self.current_structure:
            return 0.0
        
        # Usa raio de van der Waals aproximado
        vdw_radii = {
            "H": 1.2, "C": 1.7, "N": 1.55, "O": 1.52,
            "P": 1.8, "S": 1.8, "Si": 2.1, "Fe": 2.0, "Au": 1.66
        }
        
        total_area = 0.0
        for atom in self.current_structure.atoms.values():
            radius = vdw_radii.get(atom.atom_type.symbol, 1.5)
            total_area += 4 * np.pi * radius**2
        
        # Fator de correção para sobreposição
        return total_area * 0.7
    
    def _estimate_volume(self) -> float:
        """Estima volume molecular (método simplificado)"""
        if not self.current_structure:
            return 0.0
        
        # Usa raio de van der Waals aproximado
        vdw_radii = {
            "H": 1.2, "C": 1.7, "N": 1.55, "O": 1.52,
            "P": 1.8, "S": 1.8, "Si": 2.1, "Fe": 2.0, "Au": 1.66
        }
        
        total_volume = 0.0
        for atom in self.current_structure.atoms.values():
            radius = vdw_radii.get(atom.atom_type.symbol, 1.5)
            total_volume += (4/3) * np.pi * radius**3
        
        # Fator de correção para sobreposição
        return total_volume * 0.5
    
    def _to_pdb_format(self) -> str:
        """Converte para formato PDB"""
        lines = []
        lines.append(f"REMARK   Generated by AutoCura Molecular Assembly")
        lines.append(f"REMARK   {self.current_structure.name}")
        
        atom_counter = 1
        for atom in self.current_structure.atoms.values():
            x, y, z = atom.position
            lines.append(
                f"ATOM  {atom_counter:5d}  {atom.atom_type.symbol:3s} MOL     1    "
                f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00          {atom.atom_type.symbol:>2s}"
            )
            atom_counter += 1
        
        lines.append("END")
        return '\n'.join(lines)
    
    def _to_mol_format(self) -> str:
        """Converte para formato MOL (simplificado)"""
        lines = []
        lines.append(self.current_structure.name)
        lines.append("  AutoCura")
        lines.append("")
        
        atom_count = len(self.current_structure.atoms)
        bond_count = len(self.current_structure.bonds)
        lines.append(f"{atom_count:3d}{bond_count:3d}  0  0  0  0  0  0  0  0999 V2000")
        
        # Átomos
        atom_id_map = {}
        for i, (atom_id, atom) in enumerate(self.current_structure.atoms.items()):
            x, y, z = atom.position
            lines.append(
                f"{x:10.4f}{y:10.4f}{z:10.4f} {atom.atom_type.symbol:3s} 0  0  0  0  0"
            )
            atom_id_map[atom_id] = i + 1
        
        # Ligações
        for bond in self.current_structure.bonds.values():
            atom1_idx = atom_id_map.get(bond.atom1_id, 0)
            atom2_idx = atom_id_map.get(bond.atom2_id, 0)
            bond_order = int(bond.bond_type.value) if bond.bond_type.value > 0 else 1
            lines.append(f"{atom1_idx:3d}{atom2_idx:3d}{bond_order:3d}  0  0  0")
        
        lines.append("M  END")
        return '\n'.join(lines)
    
    def _dict_to_structure(self, data: Dict[str, Any]) -> MolecularStructure:
        """Converte dicionário para MolecularStructure"""
        structure = MolecularStructure(
            structure_id=data.get("id", ""),
            name=data.get("name", ""),
            molecule_type=MoleculeType(data.get("type", "organic"))
        )
        
        # Reconstrói átomos
        for atom_data in data.get("atoms", []):
            atom_type = next(
                (at for at in AtomType if at.symbol == atom_data["type"]),
                AtomType.CARBON
            )
            atom = Atom(
                atom_id=atom_data["id"],
                atom_type=atom_type,
                position=tuple(atom_data["position"]),
                charge=atom_data.get("charge", 0.0)
            )
            structure.atoms[atom.atom_id] = atom
        
        # Reconstrói ligações
        for bond_data in data.get("bonds", []):
            bond = Bond(
                bond_id=bond_data["id"],
                atom1_id=bond_data["atoms"][0],
                atom2_id=bond_data["atoms"][1],
                bond_type=BondType(bond_data["type"]),
                length=bond_data.get("length", 0.0),
                energy=bond_data.get("energy", 0.0)
            )
            structure.bonds[bond.bond_id] = bond
        
        structure.properties = data.get("properties", {})
        return structure
    
    def _parse_pdb(self, pdb_data: str) -> MolecularStructure:
        """Parse básico de formato PDB"""
        structure = MolecularStructure(
            structure_id=f"pdb_{datetime.now().timestamp()}",
            name="PDB Structure",
            molecule_type=MoleculeType.ORGANIC
        )
        
        atom_counter = 0
        for line in pdb_data.split('\n'):
            if line.startswith('ATOM') or line.startswith('HETATM'):
                atom_counter += 1
                element = line[76:78].strip()
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                
                atom_type = next(
                    (at for at in AtomType if at.symbol == element),
                    AtomType.CARBON
                )
                
                atom = Atom(
                    atom_id=f"atom_{atom_counter}",
                    atom_type=atom_type,
                    position=(x, y, z)
                )
                structure.add_atom(atom)
        
        return structure
    
    def _parse_mol(self, mol_data: str) -> MolecularStructure:
        """Parse básico de formato MOL"""
        lines = mol_data.split('\n')
        
        structure = MolecularStructure(
            structure_id=f"mol_{datetime.now().timestamp()}",
            name=lines[0].strip() if lines else "MOL Structure",
            molecule_type=MoleculeType.ORGANIC
        )
        
        # Encontra linha de contagem
        counts_line = None
        for i, line in enumerate(lines):
            if 'V2000' in line or 'V3000' in line:
                counts_line = i
                break
        
        if counts_line is None:
            return structure
        
        # Parse contagens
        atom_count = int(lines[counts_line][:3])
        bond_count = int(lines[counts_line][3:6])
        
        # Parse átomos
        atom_id_map = {}
        for i in range(atom_count):
            atom_line = lines[counts_line + 1 + i]
            x = float(atom_line[0:10])
            y = float(atom_line[10:20])
            z = float(atom_line[20:30])
            element = atom_line[31:34].strip()
            
            atom_type = next(
                (at for at in AtomType if at.symbol == element),
                AtomType.CARBON
            )
            
            atom_id = f"atom_{i+1}"
            atom = Atom(
                atom_id=atom_id,
                atom_type=atom_type,
                position=(x, y, z)
            )
            structure.add_atom(atom)
            atom_id_map[i+1] = atom_id
        
        # Parse ligações
        for i in range(bond_count):
            bond_line = lines[counts_line + 1 + atom_count + i]
            atom1_idx = int(bond_line[0:3])
            atom2_idx = int(bond_line[3:6])
            bond_order = int(bond_line[6:9])
            
            bond = Bond(
                bond_id=f"bond_{i+1}",
                atom1_id=atom_id_map.get(atom1_idx, ""),
                atom2_id=atom_id_map.get(atom2_idx, ""),
                bond_type=BondType(bond_order)
            )
            structure.add_bond(bond)
        
        return structure


class MolecularAssemblyProtocol(Protocol):
    """Protocolo para implementações específicas de montagem molecular"""
    
    def connect_to_assembler(self) -> bool:
        """Conecta ao hardware de montagem quando disponível"""
        ...
    
    def calibrate_positioning(self) -> Dict[str, Any]:
        """Calibra sistema de posicionamento atômico"""
        ...
    
    def verify_assembly(self) -> Dict[str, Any]:
        """Verifica montagem usando espectroscopia/microscopia"""
        ...
    
    def emergency_abort(self) -> bool:
        """Aborta montagem em caso de emergência"""
        ... 