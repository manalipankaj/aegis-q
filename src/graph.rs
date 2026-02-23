use std::collections::HashMap;

/// Represents the type of operation in a quantum DAG.
#[derive(Debug, Clone)]
pub enum OpType {
    Input,
    Output,
    Gate { name: String, duration_ns: f64 },
}

/// A node within the Quantum DAG.
#[derive(Debug, Clone)]
pub struct DagNode {
    pub id: usize,
    pub op: OpType,
    pub qubits: Vec<usize>,
}

/// Represents the scheduled start and end time of a node.
#[derive(Debug, Clone, Copy)]
pub struct NodeSchedule {
    pub start_time: f64,
    pub end_time: f64,
}

/// The core directed acyclic graph structure.
/// Designed for high performance in-place mutation and traversal.
#[derive(Debug, Clone, Default)]
pub struct QuantumDAG {
    pub nodes: HashMap<usize, DagNode>,
    /// Adjacency list: from_node_id -> Vec<(to_node_id, ...)>
    pub edges: HashMap<usize, Vec<(usize, usize)>>,
    pub node_counter: usize,
    /// Maps qubit_id -> last_node_id
    pub qubit_frontier: HashMap<usize, usize>,
    /// Stores the computed schedule: node_id -> NodeSchedule
    pub node_schedules: HashMap<usize, NodeSchedule>,
}

impl QuantumDAG {
    /// Creates a new, empty QuantumDAG.
    pub fn new() -> Self {
        Self {
            nodes: HashMap::new(),
            edges: HashMap::new(),
            node_counter: 0,
            qubit_frontier: HashMap::new(),
            node_schedules: HashMap::new(),
        }
    }

    /// Returns the number of nodes in the DAG.
    pub fn node_count(&self) -> usize {
        self.nodes.len()
    }

    /// Adds a gate to the DAG and updates edges using the qubit frontier.
    pub fn add_gate(&mut self, name: String, qubits: Vec<usize>, duration_ns: f64) -> usize {
        let node_id = self.node_counter;
        self.node_counter += 1;

        let op = OpType::Gate { name, duration_ns };
        let node = DagNode {
            id: node_id,
            op,
            qubits: qubits.clone(),
        };

        self.nodes.insert(node_id, node);

        for &qubit in &qubits {
            if let Some(&previous_node_id) = self.qubit_frontier.get(&qubit) {
                // Add an edge from previous_node_id to node_id
                self.edges
                    .entry(previous_node_id)
                    .or_default()
                    .push((node_id, qubit));
            }
            // Update frontier for this qubit
            self.qubit_frontier.insert(qubit, node_id);
        }

        node_id
    }

    /// Computes the start and end times for every node in the DAG.
    pub fn build_schedule(&mut self) {
        self.node_schedules.clear();
        let mut qubit_available_time: HashMap<usize, f64> = HashMap::new();

        // Since node IDs are strictly sequential and append-only,
        // we can iterate from 0 to node_counter - 1 as a topological sort.
        for node_id in 0..self.node_counter {
            if let Some(node) = self.nodes.get(&node_id) {
                // Find the maximum available time across all qubits this node acts on
                let mut start_time = 0.0;
                for &qubit in &node.qubits {
                    if let Some(&available) = qubit_available_time.get(&qubit) {
                        if available > start_time {
                            start_time = available;
                        }
                    }
                }

                // Extract duration (default to 0.0 if not a Gate)
                let duration = match &node.op {
                    OpType::Gate { duration_ns, .. } => *duration_ns,
                    _ => 0.0,
                };

                let end_time = start_time + duration;

                // Save to schedules
                self.node_schedules.insert(
                    node_id,
                    NodeSchedule {
                        start_time,
                        end_time,
                    },
                );

                // Update qubit availability tracker
                for &qubit in &node.qubits {
                    qubit_available_time.insert(qubit, end_time);
                }
            }
        }
    }

    /// Finds idle windows on qubits where the gap between operations is >= min_gap_ns.
    /// Returns a list of tuples: (qubit_id, gap_start, gap_end)
    pub fn find_idle_windows(&self, min_gap_ns: f64) -> Vec<(usize, f64, f64)> {
        let mut qubit_timelines: HashMap<usize, Vec<(f64, f64)>> = HashMap::new();

        // Iterate over all nodes and map start/end times per qubit
        for node in self.nodes.values() {
            if let Some(schedule) = self.node_schedules.get(&node.id) {
                for &qubit in &node.qubits {
                    qubit_timelines
                        .entry(qubit)
                        .or_default()
                        .push((schedule.start_time, schedule.end_time));
                }
            }
        }

        let mut idle_windows = Vec::new();

        // Sort each qubit's timeline and identify gaps
        for (&qubit, timeline) in qubit_timelines.iter_mut() {
            timeline.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());

            if timeline.len() < 2 {
                continue;
            }

            for i in 0..(timeline.len() - 1) {
                let current_interval = timeline[i];
                let next_interval = timeline[i + 1];

                let gap = next_interval.0 - current_interval.1;
                if gap >= min_gap_ns {
                    idle_windows.push((qubit, current_interval.1, next_interval.0));
                }
            }
        }

        idle_windows
    }

    /// Dynamically inserts Dynamical Decoupling (DD) sequences on idle qubits.
    pub fn apply_dd_pass(&self, sequence: &str, pulse_durations: &HashMap<usize, f64>) -> Self {
        let mut optimized_dag = QuantumDAG::new();
        let mut last_qubit_time: HashMap<usize, f64> = HashMap::new();

        for node_id in 0..self.node_counter {
            if let Some(node) = self.nodes.get(&node_id) {
                if let Some(schedule) = self.node_schedules.get(&node_id) {
                    for &qubit in &node.qubits {
                        let gap =
                            schedule.start_time - *last_qubit_time.get(&qubit).unwrap_or(&0.0);
                        
                        let pulse_dur = *pulse_durations.get(&qubit).unwrap_or(&50.0);
                        let (num_pulses, gate_sequence) = match sequence {
                            "XY4" => (4.0, vec!["DD_X", "DD_Y", "DD_X", "DD_Y"]),
                            _ => (2.0, vec!["DD_X", "DD_Y"]), // Default to standard XY
                        };
                        let threshold = num_pulses * pulse_dur * 1.5;

                        if gap >= threshold {
                            for gate_name in gate_sequence {
                                optimized_dag.add_gate(gate_name.to_string(), vec![qubit], pulse_dur);
                            }
                        }
                        last_qubit_time.insert(qubit, schedule.start_time);
                    }

                    if let OpType::Gate { name, duration_ns } = &node.op {
                        optimized_dag.add_gate(name.clone(), node.qubits.clone(), *duration_ns);
                    }

                    for &qubit in &node.qubits {
                        last_qubit_time.insert(qubit, schedule.end_time);
                    }
                }
            }
        }
        optimized_dag
    }

    /// Exports all operations in topological order for external adapters a list of tuples (name, qubits, duration).
    pub fn get_all_nodes(&self) -> Vec<(String, Vec<usize>, f64)> {
        let mut result = Vec::new();
        for node_id in 0..self.node_counter {
            if let Some(node) = self.nodes.get(&node_id) {
                if let OpType::Gate { name, duration_ns } = &node.op {
                    result.push((name.clone(), node.qubits.clone(), *duration_ns));
                }
            }
        }
        result
    }
}
