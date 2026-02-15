"""
Adaptive Boundary Protocol for One-Time Pad Allocation

Three parties (Alice, Bob, Charlie) share a pool of n one-time pads.
The algorithm dynamically adjusts region boundaries based on actual usage patterns.
"""

from typing import Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class PartyName(Enum):
    """Enumeration of parties in the protocol."""
    ALICE = "Alice"
    BOB = "Bob"
    CHARLIE = "Charlie"


@dataclass
class PartyState:
    """Tracks the state of a single party."""
    name: PartyName
    region_start: int
    region_end: int
    next_pad: int
    borrowed_pads: int = 0  # Track how many pads were borrowed

    def __repr__(self) -> str:
        return (
            f"{self.name.value}(region=[{self.region_start}, {self.region_end}], "
            f"next_pad={self.next_pad}, borrowed={self.borrowed_pads})"
        )


class AdaptiveBoundaryProtocol:
    """
    Implements the Adaptive Boundary Protocol for pad allocation.
    
    Initial Setup:
    - Alice: pads [1, ⌊n/3⌋]
    - Bob: pads [⌊n/3⌋ + d + 1, ⌊2n/3⌋]
    - Charlie: pads [⌊2n/3⌋ + d + 1, n]
    
    When a party exhausts their region, they can "borrow" k pads from an adjacent
    idle region if the gap constraint is satisfied.
    """

    def __init__(self, n: int, d: int = 1, k: int = None):
        """
        Initialize the protocol.
        
        Args:
            n: Total number of one-time pads
            d: Gap constraint (minimum spacing between regions)
            k: Number of pads to borrow at once (defaults to d)
        """
        self.n = n
        self.d = d
        self.k = k if k is not None else d
        
        # Verify constraints
        if n < 3:
            raise ValueError("Need at least 3 pads for three parties")
        if d < 1:
            raise ValueError("Gap constraint d must be >= 1")
        
        # Initialize regions for each party
        self.alice = self._init_alice()
        self.bob = self._init_bob()
        self.charlie = self._init_charlie()
        
        # Dictionary for easy access
        self.parties: Dict[PartyName, PartyState] = {
            PartyName.ALICE: self.alice,
            PartyName.BOB: self.bob,
            PartyName.CHARLIE: self.charlie,
        }
        
        # Track used pads for verification
        self.used_pads = set()
        
        # Track statistics
        self.total_messages = 0
        self.successful_messages = 0
        self.failed_messages = 0
        self.borrow_events = 0

    def _init_alice(self) -> PartyState:
        """Initialize Alice's region: [1, ⌊n/3⌋]"""
        region_start = 1
        region_end = self.n // 3
        return PartyState(
            name=PartyName.ALICE,
            region_start=region_start,
            region_end=region_end,
            next_pad=region_start,
        )

    def _init_bob(self) -> PartyState:
        """Initialize Bob's region: [⌊n/3⌋ + d + 1, ⌊2n/3⌋]"""
        region_start = (self.n // 3) + self.d + 1
        region_end = (2 * self.n) // 3
        return PartyState(
            name=PartyName.BOB,
            region_start=region_start,
            region_end=region_end,
            next_pad=region_start,
        )

    def _init_charlie(self) -> PartyState:
        """Initialize Charlie's region: [⌊2n/3⌋ + d + 1, n]"""
        region_start = (2 * self.n) // 3 + self.d + 1
        region_end = self.n
        return PartyState(
            name=PartyName.CHARLIE,
            region_start=region_start,
            region_end=region_end,
            next_pad=region_start,
        )

    def gap_constraint_satisfied(self, party: PartyState, pad_idx: int) -> bool:
        """
        Check if the gap constraint is satisfied for using a pad.
        
        The gap constraint ensures a minimum distance 'd' from adjacent regions.
        This is a simplified check; in practice, you'd verify against actual
        usage in adjacent regions.
        """
        # In this simplified version, we just check if the pad is within bounds
        # A more sophisticated version would track actual gaps from other parties
        return party.region_start <= pad_idx <= party.region_end

    def use_pad(self, party: PartyState, pad_idx: int, message: str) -> None:
        """
        Record the usage of a pad.
        
        Args:
            party: The party using the pad
            pad_idx: The pad index
            message: The message being encrypted (for logging)
        """
        if pad_idx in self.used_pads:
            raise RuntimeError(
                f"Pad {pad_idx} already used! Collision detected."
            )
        self.used_pads.add(pad_idx)

    def can_borrow(self, party: PartyState) -> Tuple[bool, Optional[PartyName]]:
        """
        Check if a party can borrow from an adjacent region.
        
        Returns:
            (can_borrow, adjacent_party_name)
        """
        if party.name == PartyName.ALICE:
            # Alice can potentially borrow from Bob
            q = self.bob
            # Check: region_end + d + k < next_pad of adjacent party
            if party.region_end + self.d + self.k < q.next_pad:
                return True, PartyName.BOB
        
        elif party.name == PartyName.BOB:
            # Bob can borrow from Alice (left) or Charlie (right)
            alice = self.alice
            if party.region_end + self.d + self.k < alice.next_pad:
                return True, PartyName.ALICE
            
            charlie = self.charlie
            if party.region_end + self.d + self.k < charlie.next_pad:
                return True, PartyName.CHARLIE
        
        elif party.name == PartyName.CHARLIE:
            # Charlie can potentially borrow from Bob
            q = self.bob
            if party.region_end + self.d + self.k < q.next_pad:
                return True, PartyName.BOB
        
        return False, None

    def extend_region(self, party: PartyState, k: int) -> None:
        """Extend a party's region by k pads."""
        new_end = party.region_end + k
        if new_end > self.n:
            new_end = self.n
        party.region_end = new_end
        party.borrowed_pads += (new_end - party.region_end)

    def send_message(self, party_name: PartyName, message: str) -> bool:
        """
        Attempt to send a message, using a pad from the party's region.
        
        Args:
            party_name: Which party is sending
            message: The message to encrypt
        
        Returns:
            True if successful, False if failed
        """
        party = self.parties[party_name]
        self.total_messages += 1
        
        # Check if we have a pad available in the current region
        if party.next_pad <= party.region_end:
            if self.gap_constraint_satisfied(party, party.next_pad):
                self.use_pad(party, party.next_pad, message)
                party.next_pad += 1
                self.successful_messages += 1
                return True
        
        # If not, try to borrow from adjacent region
        can_borrow, adjacent = self.can_borrow(party)
        if can_borrow:
            self.extend_region(party, self.k)
            self.borrow_events += 1
            # Retry the message
            return self.send_message(party_name, message)
        
        # If we can't borrow, fail
        self.failed_messages += 1
        return False

    def get_statistics(self) -> Dict:
        """Return protocol statistics."""
        total_allocated = sum(
            p.region_end - p.region_start + 1 for p in self.parties.values()
        )
        unused = total_allocated - len(self.used_pads)
        
        return {
            "total_pads": self.n,
            "total_allocated": total_allocated,
            "total_used": len(self.used_pads),
            "total_unused": unused,
            "waste_percentage": (unused / self.n * 100) if self.n > 0 else 0,
            "total_messages": self.total_messages,
            "successful_messages": self.successful_messages,
            "failed_messages": self.failed_messages,
            "borrow_events": self.borrow_events,
            "parties": {
                name.value: {
                    "region": f"[{self.parties[name].region_start}, {self.parties[name].region_end}]",
                    "pads_used": self.parties[name].next_pad - self.parties[name].region_start,
                    "pads_borrowed": self.parties[name].borrowed_pads,
                }
                for name in PartyName
            },
        }

    def print_state(self) -> None:
        """Print the current state of all parties."""
        print("=" * 70)
        print("Protocol State:")
        print("=" * 70)
        for party in self.parties.values():
            print(f"{party}")
        print("=" * 70)

    def print_statistics(self) -> None:
        """Print protocol statistics."""
        stats = self.get_statistics()
        print("\n" + "=" * 70)
        print("Protocol Statistics:")
        print("=" * 70)
        print(f"Total Pads (n):           {stats['total_pads']}")
        print(f"Total Allocated:          {stats['total_allocated']}")
        print(f"Total Used:               {stats['total_used']}")
        print(f"Total Unused (Waste):     {stats['total_unused']}")
        print(f"Waste Percentage:         {stats['waste_percentage']:.2f}%")
        print()
        print(f"Total Messages:           {stats['total_messages']}")
        print(f"Successful Messages:      {stats['successful_messages']}")
        print(f"Failed Messages:          {stats['failed_messages']}")
        print(f"Borrow Events:            {stats['borrow_events']}")
        print()
        print("Per-Party Statistics:")
        for name, party_stats in stats['parties'].items():
            print(f"  {name}:")
            print(f"    Region:       {party_stats['region']}")
            print(f"    Pads Used:    {party_stats['pads_used']}")
            print(f"    Pads Borrowed: {party_stats['pads_borrowed']}")
        print("=" * 70)


# Example usage and testing
if __name__ == "__main__":
    # Test Case 1: Equal usage
    print("\n" + "=" * 70)
    print("TEST CASE 1: Equal Usage Pattern")
    print("=" * 70)
    protocol = AdaptiveBoundaryProtocol(n=300, d=2, k=2)
    protocol.print_state()
    
    # Each party sends 30 messages
    for i in range(30):
        protocol.send_message(PartyName.ALICE, f"Alice message {i}")
        protocol.send_message(PartyName.BOB, f"Bob message {i}")
        protocol.send_message(PartyName.CHARLIE, f"Charlie message {i}")
    
    protocol.print_state()
    protocol.print_statistics()
    
    # Test Case 2: Unequal usage (one dominant sender)
    print("\n" + "=" * 70)
    print("TEST CASE 2: Unequal Usage (Alice dominates)")
    print("=" * 70)
    protocol2 = AdaptiveBoundaryProtocol(n=300, d=2, k=5)
    
    # Alice sends many messages, Bob and Charlie send few
    for i in range(80):
        protocol2.send_message(PartyName.ALICE, f"Alice message {i}")
    
    for i in range(10):
        protocol2.send_message(PartyName.BOB, f"Bob message {i}")
        protocol2.send_message(PartyName.CHARLIE, f"Charlie message {i}")
    
    protocol2.print_state()
    protocol2.print_statistics()
    
    # Test Case 3: Stress test with many messages
    print("\n" + "=" * 70)
    print("TEST CASE 3: Stress Test (many messages)")
    print("=" * 70)
    protocol3 = AdaptiveBoundaryProtocol(n=1000, d=1, k=10)
    
    success_count = 0
    for i in range(150):
        if protocol3.send_message(PartyName.ALICE, f"Message {i}"):
            success_count += 1
        if protocol3.send_message(PartyName.BOB, f"Message {i}"):
            success_count += 1
        if protocol3.send_message(PartyName.CHARLIE, f"Message {i}"):
            success_count += 1
    
    protocol3.print_statistics()
