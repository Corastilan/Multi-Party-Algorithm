from ring_sim import run_scenario


def test_large_pop():
    """Test protocol performance with large population (S.10)"""
    large_population = run_scenario(10000, 10, 15, 10)
    large_pop_percentage = ((10000 - large_population) / 10000) * 100

    # Print output for verification
    print("\n--- Test: Large party (S.10) ---")
    print(
        f"Standard (D=15) Waste: {large_population} pads | Utilization: {large_pop_percentage}%"
    )

    # Assert that the result is valid (should have some wasted pads but not all)
    assert 0 <= large_population < 10000, (
        "Large population test should produce valid waste metrics"
    )
    assert large_pop_percentage >= 0, "Utilization percentage should be non-negative"
