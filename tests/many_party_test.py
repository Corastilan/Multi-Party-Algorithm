import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.ring_sim import run_scenario

def test_large_pop():
    print("--- Test: Large party (S.10) ---")
    large_population = run_scenario(10000, 10, 15, 10)
    large_pop_percentage = ((10000 - large_population)/10000) * 100
    print(f"Standard (D=15) Waste: {large_population} pads | Utilization: {large_pop_percentage}%")

if __name__ == "__main__":
    test_large_pop()
