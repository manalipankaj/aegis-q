import cirq
from typing import List, Tuple, Any
from .base import CompilerAdapter

class CirqAdapter(CompilerAdapter):
    def __init__(self, circuit: cirq.Circuit, device_graph: list[tuple[cirq.Qid, cirq.Qid]] = None):
        self.circuit = circuit
        self.device_graph = device_graph or []
        
        # Cirq uses abstract GridQubits or LineQubits. 
        # We must map them to flat integers (0, 1, 2...) for the Rust core.
        self.qubits = sorted(list(circuit.all_qubits()))
        self.q_map = {q: i for i, q in enumerate(self.qubits)}
        self.inv_q_map = {i: q for i, q in enumerate(self.qubits)}

    def to_ir(self) -> List[Tuple[str, List[int], float]]:
        ir_payload = []
        for moment in self.circuit:
            for op in moment.operations:
                # Extract the base gate name (e.g., 'XPowGate' -> 'x')
                gate_name = op.gate.__class__.__name__.replace("PowGate", "").lower()
                qubit_indices = [self.q_map[q] for q in op.qubits]
                
                # Mocking a 50ns duration for standard operations
                duration_ns = 50.0 
                ir_payload.append((gate_name, qubit_indices, duration_ns))
                
        return ir_payload

    def get_coupling_map(self) -> List[Tuple[int, int]]:
        # Map physical Cirq device edges to our integer format
        return [(self.q_map[q1], self.q_map[q2]) for q1, q2 in self.device_graph]

    def from_optimized_ir(self, optimized_nodes: List[Any], num_qubits: int) -> cirq.Circuit:
        new_circuit = cirq.Circuit()
        
        for node in optimized_nodes:
            # Assuming your Rust core returns an object with .op, .qubits, .duration
            gate_name = node.op.lower()
            target_qubits = [self.inv_q_map[q_idx] for q_idx in node.qubits]
            
            # Reconstruct the native Cirq operations
            if gate_name in ["x", "dd_x"]:
                new_circuit.append(cirq.X(*target_qubits))
            elif gate_name in ["y", "dd_y"]:
                new_circuit.append(cirq.Y(*target_qubits))
            # ... add other standard gate mappings here ...
            
        return new_circuit