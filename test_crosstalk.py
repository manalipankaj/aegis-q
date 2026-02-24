from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.visualization import timeline_drawer
from aegis_q.adapters.qiskit_adapter import QiskitAdapter
import aegis_q

def main():
    print("--- AegisQ Pipeline Diagnostic ---")
    
    backend = GenericBackendV2(num_qubits=3)
    qc = QuantumCircuit(3)
    qc.cx(0, 1) 
    qc.delay(1500, 2) 
    qc.cx(0, 2)
    qc.cx(1, 2)
    
    adapter = QiskitAdapter(qc, backend)
    
    # CHECK 1: Did Python extract the circuit correctly?
    ir_payload = adapter.to_ir()
    print(f"\n[DIAGNOSTIC 1] Python IR Payload Length: {len(ir_payload)}")
    if len(ir_payload) > 0:
        print(f"Sample IR: {ir_payload[0]}")
    
    # Run the optimization
    optimized_qc = aegis_q.optimize_circuit(adapter, sequence="XY4")
    
    # CHECK 2: Did Python rebuild anything?
    print(f"\n[DIAGNOSTIC 2] Rebuilt Circuit Gates: {len(optimized_qc.data)}")
    
    print("\n[Optimized Circuit Architecture]")
    print(optimized_qc.draw())
    
    # Only try to schedule and draw if the circuit actually has gates!
    if len(optimized_qc.data) > 0:
        print("\nRendering Syncopated Timeline...")
        scheduled_qc = transpile(optimized_qc, backend=backend, scheduling_method="alap")
        fig = timeline_drawer(scheduled_qc, target=backend.target, show_delays=True, idle_wires=False)
        fig.savefig("crosstalk_mitigation.png", dpi=300, bbox_inches="tight")
        print("SUCCESS: Image saved!")
    else:
        print("❌ CRASH AVOIDED: Circuit is empty. The scheduler cannot process an empty circuit.")

if __name__ == "__main__":
    main()