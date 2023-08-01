from qiskit.primitives import Estimator as qiskit_estimator


class expectation:

    def __init__(self, Hamiltonian, ansatz) -> None:
        self.Hamiltonian = Hamiltonian
        self.ansatz = ansatz
        

    def calc_exp(self, parameter):
        estimator = qiskit_estimator()
        res = estimator.run(self.ansatz, self.Hamiltonian, parameter_values=parameter).result()
        self.exp = float(res.values)
        return self.exp


