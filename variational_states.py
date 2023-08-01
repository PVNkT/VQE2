from qiskit_nature.circuit.library import UCCSD, HartreeFock
from qiskit.circuit.library import RealAmplitudes, EfficientSU2, TwoLocal, ExcitationPreserving
from qiskit.circuit import QuantumCircuit, Parameter

import numpy as np

class TwoLocal_state():
    """
    Hartree Fock 상태 앞에 임의의 양자 상태를 만들 수 있는 parameterize된 양자 회로를 추가하여 Hartree Fock 상태를 보정하는 양자 상태를 만든다.
    ry, rz gate로 이루어진 층이 각각 cz들의 앞뒤에 존재하는 형식의 회로를 만든다.
        기본값으로 3번 반복하고(cz를 기준, ry, rz층은 반복수 +1번 존재), full entanglement(가능한 모든 조합을 cz gate로 연결함)를 사용한다. 4qubit의 경우 총 32개의 parameter를 사용한다.
    two-qubit reduction을 적용할 경우에 parameter수는 16개로 줄어들음 (4 qubit에서 2 qubit으로 qubit이 줄어들었기 때문)
    full 이외에 linear(인접한 qubit간에 cz gate로 연결한다.) circular (linear에서 첫 qubit과 마지막 qubit을 연결한다.)
    """

    #Hartree Fock상태를 만들고 그 앞에 임의의 양자 상태를 만드는 회로를 추가해서 양자 상태를 변화시킴
    def __init__(self, num_orbitals, num_particles, converter):
        init_state = HartreeFock(num_orbitals, num_particles, converter)
        self.ansatz = TwoLocal(num_orbitals, ['ry', 'rz'], 'cz')
        self.ansatz.compose(init_state, front=True, inplace=True)

    #회로를 반환하는 함수
    def get_state(self):
        return self.ansatz

    #회로 그림을 그림
    def draw(self):
        self.ansatz.draw("mpl")


class UCCSD_state():
    """
    Hartree Fock 상태에 e^T-T_dagger형태의 operator를 곱해서 Hartree Fock 상태를 보정한다.
    여기서 T=T_1+T_2+...의 형태로 expand되는데 이 경우에는 T_1과 T_2만을 사용해서 상태를 근사한다.
    T_1과 T_2는 생성소멸 연산자들의 곱에 어떤 상수가 붙어서 결정되는데 그 상수를 parameter로 하도록 양자 회로를 만든다.
    수소 분자의 경우에는 3개의 parameter가 필요하다.
    """
    #초기 상태를 Hartree Fock로 하는 UCCSD 양자회로를 만든다.
    def __init__(self, num_orbitals, num_particles, converter):
        init_state = HartreeFock(num_orbitals, num_particles, converter)
        ansatz = UCCSD(qubit_converter=converter, num_particles=num_particles, num_spin_orbitals=num_orbitals, initial_state=init_state)
        self.ansatz = ansatz

    #회로를 반환
    def get_state(self):
        return self.ansatz

    #회로 그림을 그림
    def draw(self):
        self.ansatz.draw("mpl")

class customH2O_state():

    def __init__(self, num_orbitals, num_particles, converter):
        self.num_MO = num_orbitals//2
        self.qc = QuantumCircuit(int(num_orbitals))
        # make HF state (bosonic)
        for i in range(num_particles[0]):
            self.qc.x(i)
    
        # bosonic excitation
        for i, j in [(2,5),(3,6),(2,6),(2,4), (1,6)]:
            theta = Parameter(f'theta_{j},{i}')*np.pi
            self.qc = self.bosonic_excitation(self.qc, j, i, theta)
            #self.qc = self.bosonic_excitation(self.qc, j+self.num_MO, i+self.num_MO, theta)
        
        # 상태를 복사
        for i in range(self.num_MO):
            self.qc.cx(i, i+self.num_MO)
        
        # non-bosonic excitation
        for i, j, k, l in [(3,6,2,5),(2,5,3,6),(2,6,3,5),(3,5,2,6)]:

            theta = Parameter(f'theta_{i},{j}_{k},{l}')*np.pi
            self.qc = self.non_bosonic_excitation(self.qc, (i,j), (k,l), theta)

        
        """
        for i in range(num_MO):
            for j in range(i):
                theta = Parameter(f'theta_{j},{i}')
                self.qc = self.bosonic_excitation(self.qc, j, i, theta)
        
        for i in range(num_MO):
            self.qc.cx(i, i+self.num_MO)
        """


    def bosonic_excitation(self, qc, low_state, high_state, theta):
        qc.sdg(low_state)
        qc.rxx(theta, low_state, high_state)
        qc.s(low_state)
        qc.sdg(high_state)
        qc.rxx(-1*theta, low_state, high_state)
        qc.s(high_state)
        return qc
    
    def non_bosonic_excitation(self, qc, up_state:tuple, down_state:tuple, theta):
        qc.sdg(up_state[0]) 
        qc.cx(up_state[0],down_state[1]+self.num_MO)
        qc.cx(up_state[0],down_state[0]+self.num_MO)
        qc.cx(up_state[0],up_state[1])
        qc.h(up_state[0])
        qc = self.non_bosonic_partial(qc, down_state[1]+self.num_MO, up_state, theta)
        qc.sdg(down_state[0]+self.num_MO)
        qc.cx(down_state[0]+self.num_MO, up_state[0])
        qc = self.non_bosonic_partial(qc, down_state[1]+self.num_MO, up_state, theta)
        qc.h(up_state[0])
        qc.cx(up_state[0],down_state[1]+self.num_MO)
        qc.cx(up_state[0],down_state[0]+self.num_MO)
        qc.cx(up_state[0],up_state[1])
        qc.s(down_state[0]+self.num_MO)
        return qc
    
    def non_bosonic_partial(self, qc, control:int, target:tuple, theta):
        
        qc.rz(theta, target[0])
        qc.cx(target[1],target[0])
        qc.rz(theta, target[0])
        qc.cx(control, target[0])
        qc.rz(-1*theta,target[0])
        qc.cx(target[1],target[0])
        qc.rz(-1*theta,target[0])
        return qc
    
    def get_state(self):
        return self.qc

    def draw(self):
        self.qc.draw("mpl")

    
