import aegis_q

def main():
    print("--- Testing AegisQ Idle Window Hunter ---")
    
    dag = aegis_q.QuantumDAG()
    
    # Q0 timeline:
    # 0->50: H
    id1 = dag.add_gate("H", [0], 50.0)
    
    # Q1 timeline:
    # 0->20: X
    id2 = dag.add_gate("X", [1], 20.0)

    # Q0 & Q1 sync at 50ns:
    # 50->150: CX
    id3 = dag.add_gate("CX", [0, 1], 100.0)

    # Delay Q0 heavily:
    # 150->600: LongGate
    id4 = dag.add_gate("Delay", [0], 450.0)
    
    # Q0 & Q1 sync at 600ns:
    # 600->700: CX
    id5 = dag.add_gate("CX", [0, 1], 100.0)

    dag.build_schedule()

    # Analysis:
    # Q1 has operations at [0, 20], [50, 150], and [600, 700].
    # Gaps for Q1: [20, 50] (length 30) and [150, 600] (length 450).
    
    # Let's search for gaps >= 100ns. It should only find the 450ns gap.
    windows = dag.find_idle_windows(100.0)
    
    print(f"Idle Windows (>100ns): {windows}")
    
    assert len(windows) == 1
    assert windows[0] == (1, 150.0, 600.0)
    
    print("SUCCESS: The Idle Window Hunter found the exact gap accurately!")

if __name__ == "__main__":
    main()
