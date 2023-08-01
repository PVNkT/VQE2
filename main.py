from omegaconf import OmegaConf

from runner import runner
from qiskit import IBMQ
import time

def main(cfg=OmegaConf.load("config.yaml")):
    #comend와 config를 합친다.
    cfg.merge_with_cli()
    #IBM 로그인을 위한 토큰 입력, 한번만 필요
    #IBMQ.save_account("token")
    #주어진 값에 대한 VQE 연산을 시행함
    vqe_result = runner(cfg)
    #연산 결과로 부터 바닥상태 에너지를 구함
    ground_E = vqe_result.get_ground_E()
    print(float(ground_E))
    print(vqe_result.parameter[-1])
    #optimizing되는 그래프 그리기
    #vqe_result.draw_optimizing()

if __name__ == "__main__":
    start = time.time()
    main()
    print("time :", time.time() - start)