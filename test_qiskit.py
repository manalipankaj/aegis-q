from qiskit import QuantumCircuit
import aegis_q


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
    adapter = aegis_q.QiskitAdapter(qc)
    optimized_qc = aegis_q.optimize_circuit(adapter)
    
    print("\n[Optimized Qiskit Circuit with AegisQ DD Pulses]")
    print(optimized_qc.draw())
    
    print("\nSUCCESS: AegisQ successfully intercepted, optimized, and returned a native Qiskit object!")

if __name__ == "__main__":
    main()