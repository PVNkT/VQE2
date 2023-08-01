from qiskit_nature.drivers import UnitsType
from qiskit_nature.drivers.second_quantization import PySCFDriver
from qiskit_nature.problems.second_quantization.electronic import ElectronicStructureProblem
from qiskit_nature.operators.second_quantization import FermionicOp
from qiskit_nature.settings import settings

class chemical_info():
    """
    molecule: name of molecule, need to be added to molecule_dict
    dict: distance between two atom (Angstrom)
    charge: total charge of molecule
    spin: total spin of molecule
    basis: basis of PySCFDriver
    """
    def __init__(self, molecule = "H2", dist = 0.74, charge = 0, spin = 0, basis ='sto3g ' ):
        #aux_operators가 dictionary 형식임을 저장함
        settings.dict_aux_operators = True
        #사용할 분자의 구조를 표현하는 부분, 필요에 따라서 추가
        molecule_dict = {"H2":f"H .0 .0 .0; H .0 .0 {dist}",
                         "HF":f"H .0 .0 .0; F .0 .0 {dist}",
                         "LiH":f"H .0 .0 .0; Li .0 .0 {dist}",
                         "H2O":"O .0 .0 .0; H 0.757 0.586 0.0; H -0.757 0.586 0.0"}
        #분자 내의 두 원자 사이의 거리로 공간상의 원자의 위치를 표현
        atom_str = molecule_dict[molecule] 
        
        #주어진 상태에 대응되는 분자 구조에 대한 정보를 불러옴
        self.driver = PySCFDriver ( atom = atom_str, unit = UnitsType. ANGSTROM , charge =charge, spin =spin, basis = basis )
        #앞서 불러온 화학적 구조에 대한 정보를 통해서 Fermiomic operator로 표현된 전기적 구조에 대한 정보(orbital수 전자의 수(up, down spin), Hamiltonian등)를 만든다.
        self.problem = ElectronicStructureProblem(self.driver)
        #second quantize된 operator를 저장한다.
        self.second_q_ops = self.problem.second_q_ops()
        #입자의 수를 저장한다. (up spin, down spin)
        self.particle_number = self.problem.grouped_property_transformed.get_property("ParticleNumber")
        #up spin을 가지는 전자의 수
        self.num_alpha = self.particle_number.num_alpha
        #down spin을 가지는 전자의 수
        self.num_beta = self.particle_number.num_beta
        #spin을 포함하는 총 orbital의 수
        self.num_orbitals = self.particle_number.num_spin_orbitals
        #operator에 대한 정보를 끝까지 다 표현한다.
        FermionicOp.set_truncation(0)

    #second quantize된 Hamiltonian을 내보내는 함수 
    def get_second_Hamiltonian(self):
        #앞서 불러온 화학적 구조에 대한 정보를 통해서 Fermiomic operator로 표현된 전기적 구조에 대한 정보를 만든다.
        main_op = self.second_q_ops['ElectronicEnergy']

        return main_op

    #입자(전자)의 수를 내보내는 함수
    def get_particle_num(self, total:bool = False):
        if total:
            #전체 전자의 수를 내보냄
            return self.num_alpha + self.num_beta
        else:
            #각 spin의 전자의 수를 tuple로 내보냄
            return self.num_alpha, self.num_beta

    #orbital의 수를 내보냄
    def get_orbital_num(self):
        return self.num_orbitals

    #기본 정보를 바탕으로 얻을 수 있는 정보(ex repulsive energy)들을 내보냄
    def get_interpret(self):
        return self.problem.interpret

if __name__ == "__main__":
    info = chemical_info(molecule = "H2O", dist = 4.03, charge = 0, spin = 0, basis ='sto3g ')    
    print(info.get_second_Hamiltonian())
