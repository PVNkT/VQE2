
from scipy.optimize import minimize


class optimizers:

    def __init__(self, calc_class, init_para) -> None:
        self.calc_class = calc_class
        self.parameter = init_para
        self.iter = 0
        self.total_iter = []
        self.parameters = []
        self.energy = []
        pass

    def scipy_min(self, method = 'COBYLA'):
        # scipy의 최소화 함수를 사용해서 최적값을 계산한다.
        result = minimize(self.calc_class.calc_exp, self.parameter, method=method, callback=self.callback)

        return result
    
    def callback(self, parameters):
        self.iter += 1
        self.total_iter.append(self.iter)
        self.parameters.append(parameters)
        self.energy.append(self.calc_class.exp)
        print(self.iter, self.calc_class.exp)


            


