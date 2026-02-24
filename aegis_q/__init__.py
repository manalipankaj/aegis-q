from typing import Optional

# 1. Import the high-performance Rust core
from ._aegis_q import QuantumDAG, AegisQError

# Adapters
from .adapters.base import CompilerAdapter
from .adapters.qiskit_adapter import QiskitAdapter

import aegis_q

def optimize_circuit(adapter, sequence="XY4"):
    # 1. Initialize and Ingest
    dag = aegis_q.QuantumDAG()
    dag.set_coupling_map(adapter.get_coupling_map())
    dag.build_from_ir(adapter.to_ir())
    dag.build_schedule()
    
    # Get physical qubit count
    num_qubits = len(adapter.circuit.qubits) if hasattr(adapter, 'circuit') else 3
    
    # 2. Optimize
    # CRITICAL: apply_dd_pass creates a NEW optimized DAG. We must capture it!
    optimized_dag = dag.apply_dd_pass(sequence, None, num_qubits)
    
    # 3. Rebuild from the OPTIMIZED nodes, not the original DAG
    optimized_nodes = optimized_dag.get_all_nodes()
    
    return adapter.from_optimized_ir(optimized_nodes, num_qubits)

# Define what gets exported when someone runs `from aegis_q import *`
__all__ = ["QuantumDAG", "AegisQError", "optimize_circuit", "CompilerAdapter", "QiskitAdapter"]