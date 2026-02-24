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
        
    def to_ir(self) -> list[tuple[str, list[int], float, dict[str, float]]]:
        """Extracts nodes (gate_name, qubits, duration) from Qiskit circuit."""
        ir_payload = []
        for instruction in self._qc.data:
            gate_name = instruction.operation.name
            qubits = tuple(self._qc.find_bit(q).index for q in instruction.qubits)
            
            duration = 50.0 
            params = {}
            
            if self._backend:
                try:
                    duration_sec = self._backend.target[gate_name][qubits].duration
                    if duration_sec is not None:
                        duration = duration_sec * 1e9  
                except (KeyError, AttributeError):
                    pass 
                    
            if gate_name == "delay":
                duration = instruction.operation.duration if instruction.operation.duration else 50.0
                
            ir_payload.append((gate_name, list(qubits), float(duration), params))
            
        return ir_payload

    def from_optimized_ir(self, optimized_nodes, num_qubits: int):
        from qiskit import QuantumCircuit
        from qiskit.circuit import Gate
        
        new_circuit = QuantumCircuit(num_qubits)
        
        for node in optimized_nodes:
            # UNPACK THE TUPLE directly! PyO3 auto-converted it for us.
            gate_name_raw, qubits, duration, params = node
            
            # Clean up the name just in case the Rust Enum formatting leaked through
            gate_name = str(gate_name_raw).lower().split('.')[-1]
            
            # DETECT THE PHYSICS: If beta is present, it's a physical microwave pulse!
            if params and "beta" in params:
                amp = params.get("amp", 0.0)
                beta = params.get("beta", 0.0)
                
                # Tag it with both the logical operation AND the physical parameters
                pulse_name = f"DRAG_{gate_name.upper()}(β={beta})"
                custom_drag = Gate(name=pulse_name, num_qubits=1, params=[])
                new_circuit.append(custom_drag, qubits)
                
            elif "cx" in gate_name:
                new_circuit.cx(qubits[0], qubits[1])
            elif "h" in gate_name:
                new_circuit.h(qubits[0])
            elif "delay" in gate_name:
                # Use the duration we just unpacked from the tuple!
                new_circuit.delay(int(duration), qubits[0], unit='dt')
            else:
                generic_gate = Gate(name=gate_name, num_qubits=len(qubits), params=[])
                new_circuit.append(generic_gate, qubits)
                
        return new_circuit

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
