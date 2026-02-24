import pytest
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from aegis_q.adapters.qiskit_adapter import QiskitAdapter
import aegis_q

@pytest.fixture
def mock_backend():
    # A standard 3-qubit backend for testing topology and scheduling
    return GenericBackendV2(num_qubits=3)

class TestAegisQCompiler:
    
    # --- 1. The Happy Path ---
    def test_standard_xy4_injection(self, mock_backend):
        """Verify that a standard delay triggers an XY4 dynamical decoupling sequence."""
        qc = QuantumCircuit(3)
        qc.cx(0, 1)
        qc.delay(1500, 2) 
        qc.cx(0, 2)
        
        adapter = QiskitAdapter(qc, mock_backend)
        optimized_qc = aegis_q.optimize_circuit(adapter, sequence="XY4")
        
        assert len(optimized_qc.data) == 7, "Failed to inject the exact number of XY4 gates."
        
        gate_names = [inst.operation.name.lower() for inst in optimized_qc.data]
        # Look for the logical X and Y embedded in the physical pulse name
        assert any("drag_dd_x" in name for name in gate_names), "Missing X-axis physical pulse."
        assert any("drag_dd_y" in name for name in gate_names), "Missing Y-axis physical pulse."

    # --- 2. The Physics Data Contract ---
    def test_drag_pulse_parameter_extraction(self, mock_backend):
        """Verify that Rust is generating and Python is extracting the physical DRAG parameters."""
        # Use a real crosstalk scenario to trigger the mitigation engine
        qc = QuantumCircuit(2)
        qc.delay(1500, 0) # Q0 idles
        qc.h(1)           # Q1 is active, causing crosstalk
        qc.cx(1, 0)
        
        adapter = QiskitAdapter(qc, mock_backend)
        optimized_qc = aegis_q.optimize_circuit(adapter, sequence="XY4")
        
        drag_gates = [inst for inst in optimized_qc.data if "DRAG" in inst.operation.name]
        assert len(drag_gates) > 0, "No physical DRAG pulses were emitted by the Rust core."
        
    # --- 3. Edge Case: The Zero-Gate Circuit ---
    def test_empty_circuit_handling(self, mock_backend):
        """Verify the compiler does not crash when handed an empty circuit."""
        qc = QuantumCircuit(3)
        
        adapter = QiskitAdapter(qc, mock_backend)
        optimized_qc = aegis_q.optimize_circuit(adapter, sequence="XY4")
        
        assert len(optimized_qc.data) == 0, "Empty circuit should return an empty circuit."

    # --- 4. Edge Case: No Idle Time ---
    def test_dense_circuit_no_injection(self, mock_backend):
        """Verify that a tightly packed circuit with no delays does not get altered."""
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 0)
        
        adapter = QiskitAdapter(qc, mock_backend)
        optimized_qc = aegis_q.optimize_circuit(adapter, sequence="XY4")
        
        # Since there is no delay, the circuit should remain exactly 3 gates
        assert len(optimized_qc.data) == 3, "Compiler improperly injected gates into a dense circuit."

    # --- 5. Edge Case: Unsupported Gates ---
    def test_unsupported_custom_gate(self, mock_backend):
        """Verify the adapter gracefully handles unknown gates without crashing the PyO3 boundary."""
        from qiskit.circuit import Gate
        qc = QuantumCircuit(1)
        qc.append(Gate(name="mystery_gate", num_qubits=1, params=[]), [0])
        
        adapter = QiskitAdapter(qc, mock_backend)
        optimized_qc = aegis_q.optimize_circuit(adapter, sequence="XY4")
        
        # The mystery gate should survive the round trip intact
        assert optimized_qc.data[0].operation.name == "mystery_gate", "Compiler dropped an unrecognized gate."