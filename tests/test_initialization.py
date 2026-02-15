import pytest
from adaptive_boundary import AdaptiveBoundaryProtocol, PartyName


def test_protocol_initialization():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    assert protocol.n == 100
    assert protocol.d == 1
    assert protocol.k == 1


def test_invalid_n():
    with pytest.raises(ValueError):
        AdaptiveBoundaryProtocol(n=2, d=1)


def test_invalid_d():
    with pytest.raises(ValueError):
        AdaptiveBoundaryProtocol(n=100, d=0)


def test_alice_region():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1)
    assert protocol.alice.region_start == 1
    assert protocol.alice.region_end == 33


def test_bob_region():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1)
    assert protocol.bob.region_start == 35
    assert protocol.bob.region_end == 66


def test_charlie_region():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1)
    assert protocol.charlie.region_start == 68
    assert protocol.charlie.region_end == 100


def test_regions_not_overlapping():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1)
    assert protocol.alice.region_end < protocol.bob.region_start
    assert protocol.bob.region_end < protocol.charlie.region_start


def test_k_defaults_to_d():
    protocol = AdaptiveBoundaryProtocol(n=100, d=3)
    assert protocol.k == 3
