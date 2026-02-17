import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.ring_sim import run_scenario

def test_latency_impact():
    print("--- Test: Latency Impact (S.4) ---")
    high_latency = run_scenario(2000, 4, 15, 4)
    zero_latency = run_scenario(2000, 4, 0, 4)
    high_lat_percentage = ((2000 - high_latency)/2000) * 100
    zero_lat_percentage = ((2000 - zero_latency) / 2000) * 100
    print(f"{'Latency (D)':<15} | {'Avg Wasted Pads':<15} | {'Utilization %':<10}")
    print(f"{'Standard (D=15)':<15}  | {high_latency:<15.2f} | {high_lat_percentage:<10.2f}%")
    print(f"{'Zero (D=0)':<15}| {zero_latency:<15.2f} | {zero_lat_percentage:<10.2f}%")

if __name__ == "__main__":
    test_latency_impact()
