from qiskit import QuantumCircuit

# 1. Import the high-performance Rust core
from ._aegis_q import QuantumDAG, AegisQError

# 2. Define the Hardware constraints
GATE_DURATIONS = {"h": 50.0, "x": 50.0, "y": 50.0, "cx": 300.0, "delay": 0.0}

# 3. The Integration Logic
def qiskit_to_aegis(qc: QuantumCircuit) -> QuantumDAG:
    dag = QuantumDAG()
    for instruction in qc.data:
        gate_name = instruction.operation.name
        qubits = [qc.find_bit(q).index for q in instruction.qubits]
        
        if gate_name == "delay":
            duration = instruction.operation.duration if instruction.operation.duration else 50.0
        else:
            duration = GATE_DURATIONS.get(gate_name, 50.0)
            
        dag.add_gate(gate_name, qubits, float(duration))
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

def optimize_circuit(qc: QuantumCircuit) -> QuantumCircuit:
    """The main entry point for AegisQ."""
    dag = qiskit_to_aegis(qc)
    dag.build_schedule()
    optimized_dag = dag.apply_dd_pass()
    return aegis_to_qiskit(optimized_dag, qc.num_qubits)

# Define what gets exported when someone runs `from aegis_q import *`
__all__ = ["QuantumDAG", "AegisQError", "optimize_circuit"]