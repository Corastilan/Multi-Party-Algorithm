import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ring_sim import run_scenario


def test_waste_within_bounds():
    cases = [
        (400, 3, 15, 1),
        (400, 3, 15, 3),
        (400, 4, 15, 1),
        (400, 4, 15, 4),
    ]

    for n, m, d, x in cases:
        waste = run_scenario(n=n, m=m, d=d, x=x)

        assert isinstance(waste, int), (
            f"waste should be int, got {type(waste)} for (n,m,d,x)={(n, m, d, x)}"
        )
        assert m * d <= waste <= n, (
            f"waste out of bounds: waste={waste}, expected [{m * d}, {n}] for (n,m,d,x)={(n, m, d, x)}"
        )
