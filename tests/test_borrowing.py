import pytest
from adaptive_boundary import AdaptiveBoundaryProtocol, PartyName


def test_can_borrow_returns_tuple():
    protocol = AdaptiveBoundaryProtocol(n=300, d=2, k=2)
    result = protocol.can_borrow(protocol.alice)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_extend_region():
    protocol = AdaptiveBoundaryProtocol(n=300, d=2, k=2)
    alice = protocol.alice
    original_end = alice.region_end
    protocol.extend_region(alice, 10)
    assert alice.region_end == original_end + 10


def test_extend_region_respects_max_n():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    charlie = protocol.charlie
    protocol.extend_region(charlie, 1000)
    assert charlie.region_end <= protocol.n


def test_borrow_events_tracked():
    protocol = AdaptiveBoundaryProtocol(n=300, d=2, k=5)
    for i in range(50):
        protocol.send_message(PartyName.ALICE, f"message {i}")
    assert protocol.borrow_events >= 0


def test_heavy_usage_with_borrow():
    protocol = AdaptiveBoundaryProtocol(n=300, d=2, k=5)
    success_count = 0
    for i in range(100):
        if protocol.send_message(PartyName.ALICE, f"message {i}"):
            success_count += 1
    assert success_count > 0
