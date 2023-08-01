
from chemical_info import chemical_info
from optimizer import optimizers
from calc_exp import expectation
import converters
import variational_states

import numpy as np
import matplotlib.pyplot as plt


class runner():
    def __init__(self, cfg):
        #어떤 분자를 사용하는지 저장
        self.molecule = cfg.molecule.molecule
        #주어진 조건에 알맞은 분자의 화학적인 구조에 대한 정보(orbital수 전자의 수(up, down spin), Hamiltonian등)을 얻음
        info = chemical_info(**cfg.molecule)#molecule = self.molecule, dist = 0.74, charge = 0, spin = 0, basis ='sto3g '
        #second quantize된 Hamiltonian operator를 저장
        operator = info.get_second_Hamiltonian()
        #입자(전자)의 수 (up spin의 수, down spin의 수)
        num_particles = info.get_particle_num()
        #spin orbital을 포함한 총 orbital의 수
        num_orbitals = info.get_orbital_num()
        #기본 정보를 바탕으로 얻을 수 있는 정보들을 포함함 (ex repulsive energy)
        interpret = info.get_interpret()
        #원하는 형태의 mapping을 골라 이를 사용하는 converter를 불러온다. 
        converter = getattr(converters, str(cfg.converter) + "_converter")()
        #convertor를 통해서 원하는 mapping을 통해서 양자 컴퓨터에 적용될 형태의 operator를 만든다.
        converted_op = converter.convert(operator, num_particles=num_particles)
        print(converted_op)
        #최적화를 적용하기 위한 parameterized 회로를 만든다. Hartree Fock 상태를 초기 상태로 하여 추가적인 parameter를 가지는 gate들을 구성하여 Hartree Fock 상태를 보정한다.
        self.ansatz = getattr(variational_states, str(cfg.state) + "_state")(num_orbitals, num_particles, converter)
        #회로를 저장한다.
        self.ansatz_circuit = self.ansatz.get_state()
        self.draw_circuit()
        #주어진 backend와 optimizer를 불러온다.
        exp_val = expectation(converted_op, self.ansatz_circuit)
        #optimizer를 저장한다.
        optimizer = optimizers(exp_val, np.zeros(self.ansatz_circuit.num_parameters))

        self.result = optimizer.scipy_min()
        self.iter = optimizer.iter
        self.energy = optimizer.energy
        self.parameter = optimizer.parameters 
        self.total_iter = optimizer.total_iter
        self.draw_optimizing()
        
    #최종 바닥 상태 에너지를 얻기 위한 함수
    def get_ground_E(self):
        return self.result.fun

    #핵간의 반발력에 의한 에너지를 반환하는 함수, 전자의 배치와는 관련이 없는 일정한 값이다.
    def get_repulsive_E(self):
        return self.vqe_result.get_repulsive_E()

    #시행 결과에 대한 모든 정보(eigenstate, eigenvalue, optimal parameter등)를 반환한다.
    def get_full_result(self):
        return self.vqe_result.get_result()

    #시행에 따라서 에너지 값이 변화하는 것을 그래프로 그려서 저장한다.
    def draw_optimizing(self):
        x = self.total_iter
        y = self.energy
        plt.figure(figsize=(10,10))
        plt.xlabel('sequence')
        plt.ylabel('enenrgy')
        plt.title(f'{self.molecule} energy optimizing')
        plt.plot(x,y)
        plt.savefig(f"result/{self.molecule} energy_plot.png")

    def draw_circuit(self):
        ansatz_circuit = self.ansatz_circuit#.decompose()
        ansatz_circuit.draw('mpl').savefig(f'result/{self.molecule}')


    
    
