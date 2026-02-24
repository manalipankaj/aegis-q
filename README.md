# AegisQ 🛡️
**High-Performance Quantum Compiler Middleware for Dynamical Decoupling**

[![PyPI version](https://badge.fury.io/py/aegis-q.svg)](https://badge.fury.io/py/aegis-q)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rust Core](https://img.shields.io/badge/Powered%20by-Rust-orange.svg)](https://www.rust-lang.org/)

AegisQ is a high-speed compiler pass designed to bridge the gap between abstract quantum circuits and noisy physical hardware. By analyzing circuit schedules and automatically injecting Dynamical Decoupling (DD) pulse sequences into idle qubit windows, AegisQ dramatically reduces decoherence and improves algorithmic fidelity.

Built with a pure **Rust** core and exposed via a zero-cost **PyO3** abstraction layer, AegisQ seamlessly integrates with standard Python frameworks like Qiskit without the typical FFI translation bottlenecks.

## ⚡ Features
* **Zero-Cost Abstraction:** Write in Python, compile in Rust. Bypasses the Python GIL for massive DAG traversal.
* **ASAP Scheduling:** Automatically calculates the critical path of your circuit to find precise nanosecond idle windows.
* **Hardware-Aware Routing (NEW in v0.2):** Reads live calibration data (T1/T2 times, gate durations) directly from IBM Qiskit `Backend` targets to calculate exact decoherence vulnerability windows.
* **Advanced DD Injection (NEW in v0.2):** Supports industry-standard dynamical decoupling sequences like **XY4** ($X-Y-X-Y$) to protect against colored thermal noise.

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
