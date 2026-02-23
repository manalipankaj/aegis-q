from qiskit import QuantumCircuit
from qiskit.providers import Backend
from typing import Optional

# 1. Import the high-performance Rust core
from ._aegis_q import QuantumDAG, AegisQError

def qiskit_to_aegis(qc: QuantumCircuit, backend: Optional[Backend] = None) -> QuantumDAG:
    dag = QuantumDAG()
    
    # 1. NEW: Extract and inject the physical hardware topology
    if backend and getattr(backend, "coupling_map", None):
        # Extract physical edges (e.g., [(0, 1), (1, 2), (1, 3)])
        edges = list(backend.coupling_map.get_edges())
        dag.set_coupling_map(edges)
        
    # 2. Existing instruction parsing...
    for instruction in qc.data:
        gate_name = instruction.operation.name
        qubits = tuple(qc.find_bit(q).index for q in instruction.qubits)
        
        duration = 50.0 
        
        if backend:
            try:
                duration_sec = backend.target[gate_name][qubits].duration
                if duration_sec is not None:
                    duration = duration_sec * 1e9  
            except (KeyError, AttributeError):
                pass 
                
        if gate_name == "delay":
            duration = instruction.operation.duration if instruction.operation.duration else 50.0
            
        dag.add_gate(gate_name, list(qubits), float(duration))
        
    return dag

def aegis_to_qiskit(dag: QuantumDAG, num_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits)
    optimized_nodes = dag.get_all_nodes() 
    
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

def optimize_circuit(qc: QuantumCircuit, backend: Optional[Backend] = None, sequence: str = "XY") -> QuantumCircuit:
    """The main entry point for AegisQ v0.2.0."""
    dag = qiskit_to_aegis(qc, backend)
    dag.build_schedule()
    
    # Map the exact pulse durations for every single qubit
    pulse_durations = {}
    if backend:
        for q in range(qc.num_qubits):
            try:
                duration_sec = backend.target["x"][(q,)].duration
                if duration_sec is not None:
                    pulse_durations[q] = duration_sec * 1e9
            except (KeyError, AttributeError):
                pulse_durations[q] = 50.0  # Fallback

    optimized_dag = dag.apply_dd_pass(
        sequence=sequence, 
        pulse_durations=pulse_durations,
        num_qubits=qc.num_qubits
    )
    return aegis_to_qiskit(optimized_dag, qc.num_qubits)

# Define what gets exported when someone runs `from aegis_q import *`
__all__ = ["QuantumDAG", "AegisQError", "optimize_circuit"]