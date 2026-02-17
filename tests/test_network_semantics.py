import random
from ring_sim import AsynchronousNetwork, RingParty

def test_network_delivery_time_and_no_self_update(monkeypatch):
    # Force randint(0, d_delay) to always return d_delay (max delay)
    monkeypatch.setattr(random, "randint", lambda a, b: b)

    d_delay = 3
    net = AsynchronousNetwork(d_delay=d_delay)
    parties = {
        1: RingParty(1, n=100, m=2, d=5),
        2: RingParty(2, n=100, m=2, d=5),
    }

    # Receiver initially sees sender at 0
    assert parties[2].view_of_others[1] == 0

    net.send_broadcast(sender_id=1, new_index=50)

    # Not delivered immediately
    assert parties[2].view_of_others[1] == 0

    # Tick fewer than delay times -> still not delivered
    for _ in range(d_delay - 1):
        delivered = net.tick(parties)
        assert delivered is False
        assert parties[2].view_of_others[1] == 0

    # Next tick reaches delivery time
    delivered = net.tick(parties)
    assert delivered is True
    assert parties[2].view_of_others[1] == 50

    # Sender should NOT “receive” its own update
    assert parties[1].view_of_others[1] == 0
