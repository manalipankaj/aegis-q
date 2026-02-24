## 🚀 AegisQ v0.3.0: Universal Pulse-Level Compiler

AegisQ is a high-performance, memory-safe quantum compiler backend written in Rust, wrapped in a flexible Python API. It mitigates $ZZ$ crosstalk and physical qubit decoherence by automatically calculating and injecting hardware-aware microwave pulse parameters (Dynamical Decoupling) into idle computational windows.

### 🏗️ Architecture



AegisQ uses a strict **Adapter Pattern** to fully decouple the physics engine from the quantum software framework. 

1. **The Python Frontend (Adapters):** Accepts native quantum circuits (e.g., `qiskit.QuantumCircuit`) and compiles them down to a Universal Intermediate Representation (IR).
2. **The PyO3 Boundary:** Safely serializes the IR and hardware topology across the language boundary.
3. **The Rust Backend (Physics Engine):** Constructs a directed acyclic graph (DAG), analyzes spatial/temporal crosstalk, calculates precise physical waveform parameters (e.g., DRAG pulse Amplitude and Beta), and injects them to protect vulnerable qubits.

### ✨ Key Features
* **Multi-Framework Support:** Universal IR supports rapid adapter creation for Qiskit, Cirq, and others.
* **Hardware-Aware Scheduling:** Prevents decoherence by utilizing $XY4$, $CPMG$, and custom dynamical decoupling sequences.
* **Leakage Prevention:** Emits precise physical DRAG envelope parameters to suppress leakage into the $|2\rangle$ state.
* **Memory Safe:** Core optimization passes are written in strict, dependency-inverted Rust.

### 💻 Quick Start

With the new Universal Architecture, you simply wrap your quantum circuit in a framework-specific adapter before handing it to the Rust physics engine.

```python
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from aegis_q.adapters.qiskit_adapter import QiskitAdapter
import aegis_q

# 1. Define your hardware and circuit
backend = GenericBackendV2(num_qubits=3)
qc = QuantumCircuit(3)
qc.cx(0, 1)
qc.delay(1500, 2) # Qubit 2 is idle and vulnerable to crosstalk
qc.cx(0, 2)

# 2. Wrap it in the AegisQ Adapter
adapter = QiskitAdapter(qc, backend)

# 3. Run the Rust Compiler Engine
# AegisQ analyzes the topology and injects physical DRAG pulses 
# (amp, beta) to protect the idle qubit.
optimized_qc = aegis_q.optimize_circuit(adapter, sequence="XY4")

print(optimized_qc.draw())
``` 

## 📦 Installation
AegisQ provides pre-compiled binaries for Linux, macOS, and Windows.

**bash**

pip install aegis-q
