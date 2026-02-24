import numpy as np
import matplotlib.pyplot as plt

def generate_drag_pulse(duration=160, amp=0.5, sigma=40, beta=0.5):
    """Generates the mathematical arrays for a microwave DRAG pulse."""
    # Center the pulse around time = 0
    t = np.arange(-duration // 2, duration // 2)
    
    # 1. The Real Component (In-Phase / I): Standard Gaussian Bell Curve
    gaussian = amp * np.exp(-(t**2) / (2 * sigma**2))
    
    # 2. The Imaginary Component (Quadrature / Q): The Derivative
    # Taking the derivative of the Gaussian to cancel out leakage frequencies
    derivative = - (t / sigma**2) * gaussian
    
    # 3. Combine them using the Beta parameter
    drag_complex = gaussian + 1j * beta * derivative
    
    return t, drag_complex.real, drag_complex.imag

def main():
    print("--- AegisQ Universal Pulse Emitter Concept ---")
    
    # Generate the pulse arrays
    t, drag_real, drag_imag = generate_drag_pulse()
    
    # Plotting the physics
    plt.figure(figsize=(10, 5))
    
    # Plot the Real (I) component
    plt.plot(t, drag_real, label='Real (Gaussian Drive)', color='blue', linewidth=2)
    
    # Plot the Imaginary (Q) component
    plt.plot(t, drag_imag, label='Imaginary (Derivative / Leakage Cancel)', color='red', linestyle='--')
    
    plt.title("DRAG Microwave Envelope (Framework Agnostic)")
    plt.xlabel("Time (dt)")
    plt.ylabel("Amplitude (Normalized)")
    plt.axhline(0, color='black', linewidth=0.5)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("microwave_envelopes.png", dpi=300)
    print("SUCCESS: Pure physics calculated! Check 'microwave_envelopes.png'.")

if __name__ == "__main__":
    main()