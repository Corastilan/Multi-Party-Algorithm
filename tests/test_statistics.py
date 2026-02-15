import pytest
from adaptive_boundary import AdaptiveBoundaryProtocol, PartyName


def test_get_statistics_returns_dict():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    stats = protocol.get_statistics()
    assert isinstance(stats, dict)


def test_statistics_has_required_keys():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    stats = protocol.get_statistics()
    assert "total_pads" in stats
    assert "total_messages" in stats
    assert "successful_messages" in stats
    assert "parties" in stats


def test_statistics_total_messages():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    for i in range(5):
        protocol.send_message(PartyName.ALICE, f"message {i}")
    stats = protocol.get_statistics()
    assert stats["total_messages"] == 5


def test_statistics_waste_percentage():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    stats = protocol.get_statistics()
    assert 0 <= stats["waste_percentage"] <= 100


def test_parties_in_statistics():
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    stats = protocol.get_statistics()
    assert "Alice" in stats["parties"]
    assert "Bob" in stats["parties"]
    assert "Charlie" in stats["parties"]


def test_print_state_doesnt_crash(capsys):
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    protocol.print_state()
    captured = capsys.readouterr()
    assert "Protocol State" in captured.out


def test_print_statistics_doesnt_crash(capsys):
    protocol = AdaptiveBoundaryProtocol(n=100, d=1, k=1)
    protocol.print_statistics()
    captured = capsys.readouterr()
    assert "Protocol Statistics" in captured.out
