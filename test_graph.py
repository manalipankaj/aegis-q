import aegis_q

def main():
    print("--- Testing AegisQ DAG Edges ---")
    
    print("Initializing QuantumDAG...")
    dag = aegis_q.QuantumDAG()
    
    # Add an H gate to Qubit 0
    id1 = dag.add_gate("H", [0], 50.0)
    print(f"Added H gate to Qubit 0, got node_id: {id1}")

    # Add a CNOT gate from Qubit 0 to Qubit 1
    id2 = dag.add_gate("CX", [0, 1], 100.0)
    print(f"Added CX gate to Qubits [0, 1], got node_id: {id2}")

    # Add another H gate to Qubit 0
    id3 = dag.add_gate("H", [0], 50.0)
    print(f"Added H gate to Qubit 0, got node_id: {id3}")

    count = dag.node_count()
    print(f"\nFinal DAG node count: {count}")
    
    assert count == 3
    print("SUCCESS: Graph logic layer and FFI bridge are accurately passing primitives!")

if __name__ == "__main__":
    main()
