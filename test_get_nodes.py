import aegis_q

def main():
    print("--- Testing get_all_nodes ---")
    dag = aegis_q.QuantumDAG()
    
    # Add a few gates
    dag.add_gate("H", [0], 50.0)
    dag.add_gate("X", [1], 20.0)
    dag.add_gate("CX", [0, 1], 100.0)
    dag.add_gate("DD_X", [0], 50.0)
    
    nodes = dag.get_all_nodes()
    
    print(f"Extracted nodes: {nodes}")
    
    assert len(nodes) == 4, "Incorrect number of nodes extracted."
    assert nodes[0] == ("H", [0], 50.0), f"Node mismatch: {nodes[0]}"
    assert nodes[1] == ("X", [1], 20.0), f"Node mismatch: {nodes[1]}"
    assert nodes[2] == ("CX", [0, 1], 100.0), f"Node mismatch: {nodes[2]}"
    assert nodes[3] == ("DD_X", [0], 50.0), f"Node mismatch: {nodes[3]}"
    print("get_all_nodes works perfectly!")

if __name__ == "__main__":
    main()
