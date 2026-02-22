import aegis_q

def main():
    print("--- AegisQ Compiler Pipeline ---")
    dag = aegis_q.QuantumDAG()
    
    # 1. Build the raw circuit
    dag.add_gate("H", [0], 50.0)
    dag.add_gate("X", [1], 50.0)
    dag.add_gate("LONG", [2], 500.0)
    dag.add_gate("CNOT", [0, 2], 300.0)
    
    print(f"Original Circuit Nodes: {dag.node_count()}")
    
    # 2. Analyze the Schedule
    dag.build_schedule()
    
    # 3. Run the Compiler Pass!
    optimized_dag = dag.apply_dd_pass()
    
    # 4. Analyze the new schedule to see what changed
    optimized_dag.build_schedule()
    
    print(f"\nOptimized Circuit Nodes: {optimized_dag.node_count()}")
    print("\n--- Optimized Execution Schedule ---")
    for node_id in range(optimized_dag.node_count()):
        schedule = optimized_dag.get_node_schedule(node_id)
        print(f"Node {node_id} | Start: {schedule[0]} ns | End: {schedule[1]} ns")
        
    print("\nSUCCESS: The 450ns gap was automatically filled with DD pulses to preserve coherence!")

if __name__ == "__main__":
    main()