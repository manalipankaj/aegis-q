import abc
from typing import List, Tuple, Dict

class CompilerAdapter(abc.ABC):
    """Abstract base class for framework-specific adapters."""
    
    @abc.abstractmethod
    def to_ir(self) -> List[Tuple[str, List[int], float]]:
        """
        Parses the native circuit and returns a universal payload:
        A list of tuples containing (gate_name, [qubit_indices], duration_ns).
        """
        pass
        
    @abc.abstractmethod
    def from_optimized_ir(self, optimized_nodes: List[Tuple[str, List[int], float]], num_qubits: int):
        """
        Reconstructs the native circuit structure from the optimized intermediate representation.
        """
        pass
        
    @abc.abstractmethod
    def get_coupling_map(self) -> List[Tuple[int, int]]:
        """
        Returns the physical hardware topology as a list of directional edges 
        (qubit_a, qubit_b). Returns an empty list if not available.
        """
        pass

    @abc.abstractmethod
    def get_pulse_durations(self, num_qubits: int) -> Dict[int, float]:
        """
        Returns a mapping of physical qubit index to its specific DD pulse duration in nanoseconds.
        Returns a default 50.0ns if not available.
        """
        pass
