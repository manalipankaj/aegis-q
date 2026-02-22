# AegisQ

AegisQ is a high-performance quantum compiler middleware, implemented in pure Rust and exposed via a zero-cost PyO3 interface. It is designed to run fast, graph-based topological optimizations on Quantum Circuits, such as Dynamical Decoupling (DD) pulse injection, prior to hardware execution.

## Fast & Safe Architecture
- **Rust Core**: Guaranteed memory safety, fearless concurrency, and zero-cost graph traversing via strictly sequential DAGs.
- **PyO3 Bridge**: Native Python integration flattening memory models across the FFI boundary using flat token primitives.
- **Python Ecosystem**: Designed to drop right into existing `qiskit` workloads natively, intercepting and optimizing backend submissions silently.

## Installation & Development
The project uses `maturin` and `pyo3`. To get started:

```bash
python -m venv .venv
source .venv/bin/activate
pip install maturin
maturin develop
```

## Running Tests
To run the included FFI boundary and algorithm logic testing scripts:
```bash
python qiskit_adapter.py
```
