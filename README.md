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

## 🚀 Quickstart (Hardware-Aware Qiskit Integration)
AegisQ acts as invisible middleware. Pass your standard Qiskit circuit and your target IBM backend through the optimizer, and AegisQ will dynamically weave protective pulses into the execution schedule.

```python
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
import aegis_q

# 1. Write your standard circuit
qc = QuantumCircuit(3)
qc.h(0)
qc.x(1)
qc.delay(1000, 2)  # Simulating a long operation on Q2
qc.cx(0, 2)

# 2. Load your target IBM Quantum hardware (or a mock simulator)
backend = GenericBackendV2(num_qubits=3)

# 3. Let AegisQ analyze the hardware schedule and inject an XY4 sequence
optimized_qc = aegis_q.optimize_circuit(qc, backend=backend, sequence="XY4")

print(optimized_qc.draw())

## 📦 Installation
AegisQ provides pre-compiled binaries for Linux, macOS, and Windows.

```bash
pip install aegis-q