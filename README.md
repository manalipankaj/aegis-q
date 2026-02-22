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
* **Automated DD Injection:** Weaves $X$ and $Y$ pulse sequences directly into vulnerability gaps before execution.
* **Qiskit Native:** Native adapter allows you to pass standard `qiskit.QuantumCircuit` objects directly into the compiler.

## 📦 Installation
AegisQ provides pre-compiled binaries for Linux, macOS, and Windows.

```bash
pip install aegis-q