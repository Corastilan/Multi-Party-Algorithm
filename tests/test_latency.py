import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ring_sim import run_scenario


def test_latency_impact():
    """Test latency impact on protocol performance (S.4)"""
    high_latency = run_scenario(2000, 4, 15, 4)
    zero_latency = run_scenario(2000, 4, 0, 4)

    high_lat_percentage = ((2000 - high_latency) / 2000) * 100
    zero_lat_percentage = ((2000 - zero_latency) / 2000) * 100

    # Print output for verification
    print("\n--- Test: Latency Impact (S.4) ---")
    print(f"{'Latency (D)':<15} | {'Avg Wasted Pads':<15} | {'Utilization %':<10}")
    print(
        f"{'Standard (D=15)':<15}  | {high_latency:<15.2f} | {high_lat_percentage:<10.2f}%"
    )
    print(f"{'Zero (D=0)':<15}| {zero_latency:<15.2f} | {zero_lat_percentage:<10.2f}%")

    # Assert that zero latency performs better than high latency
    assert zero_latency <= high_latency, (
        "Zero latency should produce less or equal wasted pads than high latency"
    )
