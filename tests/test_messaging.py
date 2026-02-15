import pytest
from adaptive_boundary import AdaptiveBoundaryProtocol, PartyName


def test_alice_send_message():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    result = protocol.send_message(PartyName.ALICE, "test message")
    assert result is True


def test_bob_send_message():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    result = protocol.send_message(PartyName.BOB, "test message")
    assert result is True


def test_charlie_send_message():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    result = protocol.send_message(PartyName.CHARLIE, "test message")
    assert result is True


def test_multiple_messages_from_one_party():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    for i in range(5):
        result = protocol.send_message(PartyName.ALICE, f"message {i}")
        assert result is True
    assert protocol.total_messages == 5


def test_next_pad_increments():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    initial_next_pad = protocol.alice.next_pad
    protocol.send_message(PartyName.ALICE, "message")
    assert protocol.alice.next_pad == initial_next_pad + 1


def test_no_pad_reuse():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    for i in range(10):
        protocol.send_message(PartyName.ALICE, f"message {i}")
    assert len(protocol.used_pads) == 10


def test_successful_message_count():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    for i in range(5):
        protocol.send_message(PartyName.ALICE, f"message {i}")
    assert protocol.successful_messages == 5
