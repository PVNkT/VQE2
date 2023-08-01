from qiskit_nature.mappers.second_quantization import ParityMapper, JordanWignerMapper, BravyiKitaevMapper
from qiskit_nature.converters.second_quantization import QubitConverter


def JW_converter(two_qubit_reduction:bool = True):
    """
    Jordan Wigner transform을 통해서 Hamiltonian과 ansatz를 qubit에 적용할 수 있는 형태로 바꾸어 준다. 각 orbital에 전자가 차있는 경우 1, 전자가 없는 경우 0
    생성 소멸 연산자는 각각 raising, lowering operator의 앞의 qubit들에 z gate를 적용하여 얻을 수 있다.
    복잡도 O(n) 
    """
    mapper = JordanWignerMapper()
    converter = QubitConverter(mapper = mapper, two_qubit_reduction=two_qubit_reduction)

    return converter

def Parity_converter(two_qubit_reduction:bool = True):
    """
    Jordan Wigner transform에서와 다르게 각 qubit이 그 qubit 앞까지 orbital이 차있는 수에 mod2를 적용한 수 (parity)를 의미한다.
    anti symmetry를 만족하기 위한 계산은 쉽게 할 수 있지만 그 qubit 뒤에 있는 qubit들을 flip해주어야 올바른 값을 얻을 수 있다.
    복잡도 O(n) 
    """
    mapper = ParityMapper()
    converter = QubitConverter(mapper = mapper, two_qubit_reduction=two_qubit_reduction)

    return converter

def BK_converter(two_qubit_reduction:bool = True):
    """
    
    """
    mapper = BravyiKitaevMapper()
    converter = QubitConverter(mapper = mapper)

    return converter



