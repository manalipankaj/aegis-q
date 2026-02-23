from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.visualization import timeline_drawer
import aegis_q

def main():
    print("--- AegisQ v1.0 Crosstalk Mitigation Test ---")
    
    # 1. Load mock hardware. This automatically generates a coupling map 
    # where Q0 is connected to Q1, and Q1 is connected to Q2.
    backend = GenericBackendV2(num_qubits=3)
    
    # 2. The Trap: Force Q0 and Q1 to sit idle at the exact same time
    qc = QuantumCircuit(3)
    qc.cx(0,1)
    
    # We delay Q2 for 1000ns. Because of the following CNOTs, 
    # Q0 and Q1 are forced to wait, creating a massive vulnerability window.
    qc.delay(1500, 2) 
    
    qc.cx(0, 2)
    qc.cx(1, 2)
    
    # 3. Run the new Staggered DD pass
    optimized_qc = aegis_q.optimize_circuit(qc, backend=backend, sequence="XY4")
    
    print("\n[Optimized Circuit Architecture]")
    print(optimized_qc.draw())
    
    # 4. Generate the Visual Proof
    print("\nRendering Syncopated Timeline...")
    fig = timeline_drawer(optimized_qc, target=backend.target, show_delays=True, idle_wires=False)
    fig.savefig("crosstalk_mitigation.png", dpi=300, bbox_inches="tight")
    
    print("SUCCESS: Check 'crosstalk_mitigation.png' to see the staggered pulses!")

if __name__ == "__main__":
    main()