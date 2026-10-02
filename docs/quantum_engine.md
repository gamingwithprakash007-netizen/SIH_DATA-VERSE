# Virtual Quantum Computer Engine

## 1. Mathematical Foundation
The DATA VERSE Virtual Quantum Computer is a software simulation developed from mathematical first principles in NumPy.

### Qubit State Representation
A single qubit state is represented in the two-dimensional Hilbert space $\mathbb{C}^2$:
$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle, \quad |\alpha|^2 + |\beta|^2 = 1$$

An $n$-qubit register resides in $\mathbb{C}^{2^n}$:
$$|\Psi\rangle = \sum_{i=0}^{2^n - 1} c_i |i\rangle, \quad \sum_{i=0}^{2^n - 1} |c_i|^2 = 1$$

### Unitary Gate Evolution
State evolution under unitary gate $U$ obeys:
$$|\Psi'\rangle = U |\Psi\rangle, \quad U^\dagger U = I$$

Supported gates: $X, Y, Z, H, S, T, S^\dagger, T^\dagger, R_x(\theta), R_y(\theta), R_z(\theta), P(\phi), \text{CNOT}, \text{CZ}, \text{SWAP}$.

### Projective Measurement
Computational basis measurements sample basis states $|i\rangle$ with Born rule probability $P(i) = |c_i|^2$.
