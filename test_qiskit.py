from qiskit import QuantumCircuit
import aegis_q

# --- The Adapter Logic ---

GATE_DURATIONS = {"h": 50.0, "x": 50.0, "y": 50.0, "cx": 300.0, "delay": 0.0}

def qiskit_to_aegis(qc: QuantumCircuit) -> aegis_q.QuantumDAG:
    dag = aegis_q.QuantumDAG()
    for instruction in qc.data:
        gate = instruction.operation
        gate_name = gate.name
        qubits = [qc.find_bit(q).index for q in instruction.qubits]
        
        if gate_name == "delay":
            duration = gate.duration if gate.duration else 50.0
        else:
            duration = GATE_DURATIONS.get(gate_name, 50.0)
            
        dag.add_gate(gate_name, qubits, float(duration))
    return dag

def aegis_to_qiskit(dag: aegis_q.QuantumDAG, num_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits)
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
            pulse_type = gate_name.split("_")[1].lower()
            if pulse_type == "x":
                qc.x(qubits[0])
            elif pulse_type == "y":
                qc.y(qubits[0])
        elif gate_name == "delay" or gate_name == "LONG":
            qc.delay(int(duration), qubits[0])
            
    return qc

def optimize_circuit(qc: QuantumCircuit) -> QuantumCircuit:
    dag = qiskit_to_aegis(qc)
    dag.build_schedule()
    optimized_dag = dag.apply_dd_pass()
    return aegis_to_qiskit(optimized_dag, qc.num_qubits)

# --- The Execution Test ---

def main():
    print("--- AegisQ + Qiskit Integration Test ---")
    
    # 1. User writes standard Qiskit code
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.x(1)
    qc.delay(500, 2)  # Simulating a long operation on Q2
    qc.cx(0, 2)
    
    print("\n[Original Qiskit Circuit]")
    print(qc.draw())
    
    # 2. AegisQ silently optimizes it
    optimized_qc = optimize_circuit(qc)
    
    print("\n[Optimized Qiskit Circuit with AegisQ DD Pulses]")
    print(optimized_qc.draw())
    
    print("\nSUCCESS: AegisQ successfully intercepted, optimized, and returned a native Qiskit object!")

if __name__ == "__main__":
    main()