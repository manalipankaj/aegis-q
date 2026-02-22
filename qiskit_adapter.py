from qiskit import QuantumCircuit
import aegis_q

# A mock lookup table for hardware gate durations (in nanoseconds)
# In a production tool, this would be dynamically pulled from an IBM backend's properties.
GATE_DURATIONS = {
    "h": 50.0,
    "x": 50.0,
    "y": 50.0,
    "cx": 300.0,
    "delay": 0.0, # Handled dynamically based on user input
}

def qiskit_to_aegis(qc: QuantumCircuit) -> aegis_q.QuantumDAG:
    """Parses a Qiskit QuantumCircuit into the high-performance Rust AegisQ DAG."""
    dag = aegis_q.QuantumDAG()
    
    for instruction in qc.data:
        gate = instruction.operation
        gate_name = gate.name
        
        # Map Qiskit's qubit objects to flat integer indices
        qubit_indices = [qc.find_bit(q).index for q in instruction.qubits]
        
        # Determine duration
        if gate_name == "delay":
            duration = gate.duration if gate.duration else 50.0
        else:
            duration = GATE_DURATIONS.get(gate_name, 50.0) # Default to 50ns if unknown
            
        # Pass the flat primitives across the FFI boundary into Rust
        dag.add_gate(gate_name, qubit_indices, duration)
        
    return dag

def aegis_to_qiskit(dag: aegis_q.QuantumDAG, num_qubits: int) -> QuantumCircuit:
    """Rebuilds a Qiskit QuantumCircuit from an optimized AegisQ DAG."""
    qc = QuantumCircuit(num_qubits)
    
    # We need to extract the optimized nodes from Rust.
    # We will need to add a small helper method to Rust to export the nodes in order.
    # For now, let's assume `dag.get_all_nodes()` returns a list of (name, [qubits], duration)
    
    optimized_nodes = dag.get_all_nodes() 
    
    for gate_name, qubits, duration in optimized_nodes:
        if gate_name == "h":
            qc.h(qubits[0])
        elif gate_name == "x":
            qc.x(qubits[0])
        elif gate_name == "y":
            qc.y(qubits[0])
        elif gate_name == "cx":
            qc.cx(qubits[0], qubits[1])
        elif gate_name.startswith("DD_"):
            # It's our injected Dynamical Decoupling pulse!
            pulse_type = gate_name.split("_")[1].lower()
            if pulse_type == "x":
                qc.x(qubits[0])
            elif pulse_type == "y":
                qc.y(qubits[0])
        elif gate_name == "LONG" or gate_name == "delay":
            qc.delay(int(duration), qubits[0])
            
    return qc

def optimize_circuit(qc: QuantumCircuit) -> QuantumCircuit:
    """The main entry point for the user."""
    # 1. Ingest
    dag = qiskit_to_aegis(qc)
    
    # 2. Analyze & Mutate (in pure Rust)
    dag.build_schedule()
    optimized_dag = dag.apply_dd_pass()
    
    # 3. Emit
    return aegis_to_qiskit(optimized_dag, qc.num_qubits)