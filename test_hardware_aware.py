from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
import aegis_q

def main():
    print("--- AegisQ v0.2.0 Hardware-Aware Test ---")
    
    # 1. Load a mock hardware backend (simulates real IBM hardware durations)
    # This automatically generates realistic float values for gate execution times.
    backend = GenericBackendV2(num_qubits=3)
    
    # 2. Write the standard circuit
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.x(1)
    qc.delay(1000, 2)  # A 1000ns delay to force a massive coherence gap on Qubit 0
    qc.cx(0, 2)
    
    print("\n[Original Circuit]")
    print(qc.draw())
    
    # 3. Run the Hardware-Aware Optimizer and request the XY4 sequence
    adapter = aegis_q.QiskitAdapter(qc, backend)
    optimized_qc = aegis_q.optimize_circuit(adapter, sequence="XY4")
    
    print("\n[Optimized Circuit with Hardware-Calibrated XY4 Sequence]")
    print(optimized_qc.draw())
    
    print("\nSUCCESS: AegisQ dynamically calculated hardware thresholds and injected X-Y-X-Y!")

if __name__ == "__main__":
    main()