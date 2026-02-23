use std::collections::HashMap;
use pyo3::create_exception;
use pyo3::prelude::*;

pub mod graph;

// Define a custom Python exception for AegisQ errors
create_exception!(aegis_q, AegisQError, pyo3::exceptions::PyException);

/// Python wrapper for the core QuantumDAG.
#[pyclass(name = "QuantumDAG", unsendable)]
pub struct PyQuantumDAG {
    inner: graph::QuantumDAG,
}

impl Default for PyQuantumDAG {
    fn default() -> Self {
        Self::new()
    }
}

#[pymethods]
impl PyQuantumDAG {
    /// Creates a new, empty QuantumDAG.
    #[new]
    pub fn new() -> Self {
        PyQuantumDAG {
            inner: graph::QuantumDAG::new(),
        }
    }

    pub fn set_coupling_map(&mut self, edges: Vec<(usize, usize)>) {
        self.inner.set_coupling_map(edges);
    }

    /// Returns the total number of nodes in the DAG.
    pub fn node_count(&self) -> usize {
        self.inner.node_count()
    }

    /// Adds a gate node to the graph and connects dependent edges.
    pub fn add_gate(&mut self, name: String, qubits: Vec<usize>, duration_ns: f64) -> usize {
        self.inner.add_gate(name, qubits, duration_ns)
    }

    /// Computes the schedule (start and end times) for all nodes.
    pub fn build_schedule(&mut self) {
        self.inner.build_schedule();
    }

    /// Retrieves the schedule for a specific node as (start_time, end_time).
    pub fn get_node_schedule(&self, node_id: usize) -> Option<(f64, f64)> {
        self.inner
            .node_schedules
            .get(&node_id)
            .map(|sched| (sched.start_time, sched.end_time))
    }

    /// Finds idle windows on qubits where the gap between operations is >= min_gap_ns.
    pub fn find_idle_windows(&self, min_gap_ns: f64) -> Vec<(usize, f64, f64)> {
        self.inner.find_idle_windows(min_gap_ns)
    }

    /// Dynamically inserts Dynamical Decoupling (DD) sequences on idle qubits.
    #[pyo3(signature = (sequence="XY", pulse_durations=None, num_qubits=0))]
    pub fn apply_dd_pass(&self, sequence: &str, pulse_durations: Option<HashMap<usize, f64>>, num_qubits: usize) -> Self {
        // Safely unwrap the Option from Python. If None, create an empty HashMap.
        let durations = pulse_durations.unwrap_or_default();
        
        Self {
            // Now pass the guaranteed HashMap and the num_qubits to the inner core
            inner: self.inner.apply_dd_pass(sequence, durations, num_qubits),
        }
    }

    /// Exports all operations in topological order a list of tuples (name, qubits, duration).
    pub fn get_all_nodes(&self) -> Vec<(String, Vec<usize>, f64)> {
        self.inner.get_all_nodes()
    }
}

/// The AegisQ high-performance quantum compiler module.
#[pymodule]
fn _aegis_q(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register the custom exception
    m.add("AegisQError", _py.get_type::<AegisQError>())?;

    // Register classes
    m.add_class::<PyQuantumDAG>()?;

    Ok(())
}