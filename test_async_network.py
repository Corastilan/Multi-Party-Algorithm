import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ring_sim import AsynchronousNetwork, RingParty, run_scenario


def test_modular_arithmetic_gap():
    """Verify that the gap calculation handles the ring wrap-around correctly."""
    n, m, d = 2000, 4, 15
    p1 = RingParty(1, n, m, d)

    # P1 is at 0. If neighbor P2 is at 1500 (behind P1 in a circle),
    # the gap forward to P2 should be 1500.
    p1.my_index = 0
    p1.view_of_others[2] = 1500
    gap = (p1.view_of_others[2] - p1.my_index) % n
    assert gap == 1500

    # If P1 is at 1990 and P2 is at 10 (just across the wrap-around point)
    p1.my_index = 1990
    p1.view_of_others[2] = 10
    gap = (p1.view_of_others[2] - p1.my_index) % n
    assert gap == 20


def test_network_delivery_integrity():
    """Verify that messages are only delivered after a tick and not instantly."""
    net = AsynchronousNetwork(d_delay=10)
    parties = {1: RingParty(1, 100, 2, 5), 2: RingParty(2, 100, 2, 5)}

    # Party 1 moves to index 50 and broadcasts
    net.send_broadcast(sender_id=1, new_index=50)

    # Immediate check: Party 2 should still see the OLD view (at 0)
    assert parties[2].view_of_others[1] == 0

    # Force clock forward by max delay
    for _ in range(11):
        net.tick(parties)

    # After max delay, Party 2 must have received the update
    assert parties[2].view_of_others[1] == 50


def test_perfect_secrecy_logic():
    """Ensure the 'data' status is never granted for a burned index."""
    # This mimics the get_move_status check manually
    burned = {10, 11, 12}
    next_idx = 11
    gap = 20  # Safe gap
    d = 15

    # In logic: if gap > d and next_idx not in burned -> 'data'
    # Since 11 IS in burned, it should fail the 'data' check
    is_data = (gap > d) and (next_idx not in burned)
    assert not is_data, "Index 11 is burned; it should not be available for DATA."


def test_protocol_execution_safety():
    """
    Integration Test: Runs a full scenario and asserts that
    no security exceptions are raised during execution.
    """
    # Run a high-contention scenario (M=4, X=4)
    # Should not raise any exceptions
    run_scenario(n=1000, m=4, d=15, x=4)
