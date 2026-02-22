import aegis_q

def main():
    print("--- Testing AegisQ topological scheduling ---")
    
    print("Initializing QuantumDAG...")
    dag = aegis_q.QuantumDAG()
    
    # Add an H gate to Qubit 0 (Starts at 0, Takes 50ns)
    id1 = dag.add_gate("H", [0], 50.0)
    
    # Add an X gate to Qubit 1 (Starts at 0, Takes 20ns)
    id2 = dag.add_gate("X", [1], 20.0)

    # Add a CNOT gate from Qubit 0 to Qubit 1
    # Both Qubit 0 and 1 must be free.
    # Q0 is free at 50, Q1 is free at 20.
    # CNOT must start at max(50, 20) = 50. 
    id3 = dag.add_gate("CX", [0, 1], 100.0)

    # Compute the schedule!
    print("\nBuilding analytical schedule...")
    dag.build_schedule()

    node1_time = dag.get_node_schedule(id1)
    node2_time = dag.get_node_schedule(id2)
    node3_time = dag.get_node_schedule(id3)

    print(f"Node 0 (H on q0): Start={node1_time[0]}, End={node1_time[1]}")
    print(f"Node 1 (X on q1): Start={node2_time[0]}, End={node2_time[1]}")
    print(f"Node 2 (CX on q0,q1): Start={node3_time[0]}, End={node3_time[1]}")
    
    assert node3_time[0] == 50.0
    print("\nSUCCESS: The topological sort properly delayed the CNOT gate until both qubits were idle!")

if __name__ == "__main__":
    main()
