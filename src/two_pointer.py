import random
import statistics


class AsynchronousNetwork:
    """
    Simulates an asynchronous network of nodes with variable delay.
    Broadcast updates the current position of a party to all members.
    Tick acts as the global clock and decides the delivery of messages.
    """

    def __init__(self, d_delay):
        self.d_delay = d_delay
        self.queue = []
        self.current_time = 0

    def send_broadcast(self, sender_id, new_index):
        """Broadcast a pad position update to all parties."""
        delivery_time = self.current_time + random.randint(0, self.d_delay)
        self.queue.append((delivery_time, sender_id, new_index))

    def tick(self, parties):
        """Process the global clock tick and deliver pending messages."""
        self.current_time += 1
        delivered = []
        remaining = []
        for msg in self.queue:
            if msg[0] <= self.current_time:
                delivered.append(msg)
            else:
                remaining.append(msg)
        self.queue = remaining
        for _, sender_id, idx in delivered:
            for p_id, party in parties.items():
                if p_id != sender_id:
                    party.update_view(sender_id, idx)
        return len(delivered) > 0


class TwoPointerParty:
    """
    Represents a single participant in the m-party OTP protocol.

    Uses a two-pointer model:
    - Odd-indexed parties (1, 3, 5, ...) approach from the left (forward)
    - Even-indexed parties (2, 4, 6, ...) approach from the right (backward)

    This allows multiple parties to effectively use the same pad pool without
    wasteful static partitioning.

    Responsibilities:
    1. Local State Management: Tracks the party's current pointer (my_index)
       within the N-sized cryptographic buffer.
    2. Distributed Awareness: Maintains a 'view_of_others' dictionary, which
       is a local map of all other parties' positions.
    3. Asynchronous Handling: Updates the local map only when a broadcast
       is received from the network, simulating real-world communication lag.
    4. Security Enforcement: Used by the main logic to ensure a safety
       buffer (D) exists between this party's pointer and the closest known
       positions of other parties.
    """

    def __init__(self, party_id, n, m, d):
        self.party_id = party_id
        self.n, self.m, self.d = n, m, d
        self.direction = (
            1 if party_id % 2 == 1 else -1
        )  # 1 for forward, -1 for backward

        # odd parties start at 0, even parties start at n-1
        if party_id % 2 == 1:
            self.my_index = 0
        else:
            self.my_index = n - 1

        self.view_of_others = {}
        for i in range(1, m + 1):
            if i != party_id:
                if i % 2 == 1:
                    self.view_of_others[i] = 0
                else:
                    self.view_of_others[i] = n - 1

        self.pads_used = 0

    def update_view(self, sender_id, index):
        """Update the known position of another party."""
        self.view_of_others[sender_id] = index

    def get_closest_opponent(self) -> int:
        """
        Get the position of the closest party moving in the opposite direction.
        For safety, we use the most conservative (closest) estimate.
        """
        closest = None
        min_distance = float("inf")

        for party_id, position in self.view_of_others.items():
            if (self.direction == 1 and party_id % 2 == 0) or (
                self.direction == -1 and party_id % 2 == 1
            ):
                if self.direction == 1:
                    distance = (position - self.my_index) % self.n
                else:
                    distance = (self.my_index - position) % self.n

                if distance < min_distance:
                    min_distance = distance
                    closest = position

        return closest if closest is not None else None


def run_scenario(n, m, d, x):
    """
    Main simulation loop for a specific m-party configuration using two-pointer model.

    Logic Flow:
    1. Initialization: Odd parties start at 0 moving forward, even parties start at n-1 moving backward.
    2. The Burned set: Initializes a set to track used OTPs.
    3. Priority-Based Execution:
       - Priority 1 (Data): Active senders consume fresh pads if the gap is safe.
       - Priority 2 (Drift): Senders skip 'Dead' pads to find fresh ones.
       - Priority 3 (Yield): Silent parties jump forward/backward to clear space for others.
    4. Termination: Breaks when a 'Clinch' state is reached (no one can move
       and no broadcasts are pending).

    Returns: The count of wasted (unused) pads.
    """
    network = AsynchronousNetwork(d)
    all_ids = list(range(1, m + 1))
    active_ids = random.sample(all_ids, x)
    silent_ids = [i for i in all_ids if i not in active_ids]
    parties = {i: TwoPointerParty(i, n, m, d) for i in range(1, m + 1)}

    burned = set(parties[pid].my_index for pid in active_ids)

    MAX_UTILIZATION = n - (m * d)

    iteration_count = 0
    max_iterations = n * 10

    while len(burned) < MAX_UTILIZATION and iteration_count < max_iterations:
        iteration_count += 1
        network.tick(parties)

        def get_move_status(p_id):
            """
            Returns:
            ('data', next_index) if next pad is fresh and gap is safe.
            ('drift', next_index) if next pad is burned but gap is safe.
            (None, None) if gap is unsafe (blocked by opponent or no valid move).
            """
            p = parties[p_id]

            # Calculate next position
            next_idx = (p.my_index + p.direction) % n

            # Get closest opponent in opposite direction
            closest_opponent = p.get_closest_opponent()

            if closest_opponent is None:
                return None, None

            if p.direction == 1:
                gap = (closest_opponent - p.my_index) % n
            else:
                gap = (p.my_index - closest_opponent) % n

            if gap <= d:
                return None, None

            if next_idx not in burned:
                return "data", next_idx
            else:
                return "drift", next_idx

        moved_in_tick = False

        legal_senders = [
            pid for pid in active_ids if get_move_status(pid)[0] is not None
        ]
        if legal_senders:
            sid = random.choice(legal_senders)
            status, nxt = get_move_status(sid)

            parties[sid].my_index = nxt
            if status == "data":
                burned.add(nxt)
                parties[sid].pads_used += 1

            # Broadcast the new position
            network.send_broadcast(sid, nxt)
            moved_in_tick = True

        else:
            legal_jumpers = [
                pid for pid in silent_ids if get_move_status(pid)[0] is not None
            ]
            if legal_jumpers:
                jid = random.choice(legal_jumpers)
                status, nxt = get_move_status(jid)
                parties[jid].my_index = nxt
                network.send_broadcast(jid, nxt)
                moved_in_tick = True

        if not moved_in_tick and not network.queue:
            break

    wasted_pads = n - len(burned)
    return wasted_pads


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Two-Pointer Results:")
    print("=" * 70)

    for M in [3, 4]:
        N, D = 2000, 15
        TRIALS = 50
        print(f"\n--- Two-Pointer Protocol (M={M}, N={N}, D={D}) ---")
        print(f"Theoretical naive bound: {(M - 1) / M * N:.0f} pads wasted")
        print(
            f"{'Scenario (S.x)':<15} | {'Avg Wasted':<15} | {'Utilization %':<15} | {'Improvement':<12}"
        )
        print("-" * 70)

        naive_waste = (M - 1) / M * N

        for x in range(1, M + 1):
            results = [run_scenario(N, M, D, x) for _ in range(TRIALS)]
            avg_waste = statistics.mean(results)
            std_dev = statistics.stdev(results) if len(results) > 1 else 0
            utilization = ((N - avg_waste) / N) * 100
            improvement = (
                ((naive_waste - avg_waste) / naive_waste) * 100
                if naive_waste > 0
                else 0
            )

            print(
                f"S.{x:<13} | {avg_waste:<15.2f} | {utilization:<15.2f}% | {improvement:+.1f}%"
            )

    print("\n" + "=" * 70)
