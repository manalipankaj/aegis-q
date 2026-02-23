from typing import Optional

# 1. Import the high-performance Rust core
from ._aegis_q import QuantumDAG, AegisQError

# Adapters
from .adapters.base import CompilerAdapter
from .adapters.qiskit_adapter import QiskitAdapter

def optimize_circuit(adapter: CompilerAdapter, sequence: str = "XY"):
    """
    The main entry point for AegisQ.
    
    Args:
        adapter (CompilerAdapter): The framework-specific adapter.
        sequence (str, optional): The DD sequence to apply (e.g., 'XY', 'XY4'). Defaults to 'XY'.
        
    Returns:
        The optimized native circuit reconstructed by the adapter.
    """
    dag = QuantumDAG()
    
    # Setup mapping
    dag.set_coupling_map(adapter.get_coupling_map())
    
    # Quickly build the schedule natively in Rust
    dag.build_from_ir(adapter.to_ir())
    dag.build_schedule()
    
    # Fetch pulse durations
    num_qubits = len(adapter.get_pulse_durations(0)) if hasattr(adapter._qc, 'num_qubits') else 0
    if num_qubits == 0:
        # Fallback check assuming adapter._qc is available for extraction
         num_qubits = getattr(adapter, "_qc").num_qubits if hasattr(adapter, "_qc") else 0
    
    pulse_durations = adapter.get_pulse_durations(num_qubits)

    optimized_dag = dag.apply_dd_pass(
        sequence=sequence, 
        pulse_durations=pulse_durations,
        num_qubits=num_qubits
    )
    return adapter.from_optimized_ir(optimized_dag.get_all_nodes(), num_qubits)

# Define what gets exported when someone runs `from aegis_q import *`
__all__ = ["QuantumDAG", "AegisQError", "optimize_circuit", "CompilerAdapter", "QiskitAdapter"]