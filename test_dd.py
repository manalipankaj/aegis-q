import aegis_q

def main():
    print("--- Testing apply_dd_pass ---")
    dag = aegis_q.QuantumDAG()
    
    # Node 0: H on Q0 (0ns to 50ns)
    n0 = dag.add_gate("H", [0], 50.0)
    # Node 1: X on Q1 (0ns to 50ns)
    n1 = dag.add_gate("X", [1], 50.0)
    
    # Node 2: Long Gate on Q2 (0ns to 500ns)
    n2 = dag.add_gate("LONG", [2], 500.0)
    
    # Node 3: CNOT on Q0 and Q2 (Should force Q0 to wait until 500ns)
    n3 = dag.add_gate("CNOT", [0, 2], 300.0)
    
    # Build schedule first to compute the start and end times
    dag.build_schedule()

    print(f"Original DAG nodes: {dag.node_count()}")
    
    # Apply DD pass
    opt_dag = dag.apply_dd_pass()
    opt_dag.build_schedule()
    
    print(f"Optimized DAG nodes: {opt_dag.node_count()}")
    
    for i in range(opt_dag.node_count()):
        sched = opt_dag.get_node_schedule(i)
        print(f"Opt Node {i} | Start: {sched[0]} | End: {sched[1]}")
        
    assert opt_dag.node_count() > dag.node_count(), "DD pass failed to insert nodes."
    print("Test passed successfully.")

if __name__ == "__main__":
    main()
