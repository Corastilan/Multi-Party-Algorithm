import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from KujuluvaGanesh_Then_Davila_4_protocol import run_scenario


def test_run_scenario_reproducible_with_seed():
    n, m, d, x = 600, 4, 15, 4

    random.seed(12345)
    w1 = run_scenario(n=n, m=m, d=d, x=x)

    random.seed(12345)
    w2 = run_scenario(n=n, m=m, d=d, x=x)

    assert w1 == w2
