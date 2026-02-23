import abc
from typing import List, Tuple, Dict, Optional
from qiskit import QuantumCircuit
from qiskit.providers import Backend
from .base import CompilerAdapter

class QiskitAdapter(CompilerAdapter):
    """Adapter for compiling Qiskit circuits in AegisQ."""
    
    def __init__(self, qc: QuantumCircuit, backend: Optional[Backend] = None):
        self._qc = qc
        self._backend = backend
        
    def to_ir(self) -> List[Tuple[str, List[int], float]]:
        """Extracts nodes (gate_name, qubits, duration) from Qiskit circuit."""
        nodes = []
        for instruction in self._qc.data:
            gate_name = instruction.operation.name
            qubits = tuple(self._qc.find_bit(q).index for q in instruction.qubits)
            
            duration = 50.0 
            
            if self._backend:
                try:
                    duration_sec = self._backend.target[gate_name][qubits].duration
                    if duration_sec is not None:
                        duration = duration_sec * 1e9  
                except (KeyError, AttributeError):
                    pass 
                    
            if gate_name == "delay":
                duration = instruction.operation.duration if instruction.operation.duration else 50.0
                
            nodes.append((gate_name, list(qubits), float(duration)))
            
        return nodes

    def from_optimized_ir(self, optimized_nodes: List[Tuple[str, List[int], float]], num_qubits: int) -> QuantumCircuit:
        """Reconstructs the optimized QuantumCircuit."""
        qc = QuantumCircuit(num_qubits)
        
        for gate_name, qubits, duration in optimized_nodes:
            if gate_name in ["h", "x", "y"]:
                getattr(qc, gate_name)(qubits[0])
            elif gate_name == "cx":
                qc.cx(qubits[0], qubits[1])
            elif gate_name.startswith("DD_"):
                getattr(qc, gate_name.split("_")[1].lower())(qubits[0])
            elif gate_name in ["delay", "LONG"]:
                qc.delay(int(duration), qubits[0])
                
        return qc

    def get_coupling_map(self) -> List[Tuple[int, int]]:
        """Returns the hardware topology."""
        if self._backend and getattr(self._backend, "coupling_map", None):
             return list(self._backend.coupling_map.get_edges())
        return []

    def get_pulse_durations(self, num_qubits: int) -> Dict[int, float]:
        """Gets exact calibration data for the DD pulses."""
        pulse_durations = {}
        for q in range(num_qubits):
            try:
                if self._backend:
                    duration_sec = self._backend.target["x"][(q,)].duration
                    if duration_sec is not None:
                        pulse_durations[q] = duration_sec * 1e9
                        continue
            except (KeyError, AttributeError):
                pass
            pulse_durations[q] = 50.0  # Fallback
        return pulse_durations
