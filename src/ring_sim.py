import random
import statistics


class AsynchronousNetwork:
    """
    Simulates an asynchronous network of nodes with
    variable delay. Broadcast updates the current position
    of the party to all members. Tick acts as the
    global clock and decides the delivery of messages.
    """
    def __init__(self, d_delay):
        self.d_delay = d_delay
        self.queue = []
        self.current_time = 0

    def send_broadcast(self, sender_id, new_index):
        delivery_time = self.current_time + random.randint(0, self.d_delay)
        self.queue.append((delivery_time, sender_id, new_index))

    def tick(self, parties):
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


class RingParty:
    """
    Represents a single node in the OTP ring. Tracks the positions of
    all nodes in the ring through view_of_others and my_index. Updates
    positions when receiving broadcast messages. Ensures there exists a
    gap of D between my_index and last position of neighbours
    """
    def __init__(self, party_id, n, m, d):
        self.party_id = party_id
        self.n, self.m, self.d = n, m, d
        self.my_index = (party_id - 1) * (n // m)
        self.view_of_others = {i + 1: (i * (n // m)) for i in range(m)}
        self.pads_used = 0

    def update_view(self, sender_id, index):
        self.view_of_others[sender_id] = index


def run_scenario(n, m, d, x):
    """
    Simulation loop for a specific ring configuration.
    1. Initializes party positions and categorizes as 'Active' and 'Silent' parties.
    2. Uses a burned set to track used OTPs
    3. Moves are categorized into three types:
        - 'Data': Active senders consume fresh pads if the gap is safe
        - 'Drift': Senders skip used pads to find fresh ones
        - 'Yield': Silent parties jump forward to clear space for others
    4. Terminates when a 'Clinch' state is reached, i.e., no one can move and no broadcasts
    are pending.

    Returns the count of unused pads.
    """
    network = AsynchronousNetwork(d)
    all_ids = list(range(1, m + 1))
    active_ids = random.sample(all_ids, x)
    silent_ids = [i for i in all_ids if i not in active_ids]
    parties = {i: RingParty(i, n, m, d) for i in range(1, m + 1)}

    # Initially, we only burn the starting positions of the ACTIVE IDs to track progress
    burned = set(parties[pid].my_index for pid in active_ids)
    MAX_UTILIZATION = n - (m * d)

    while len(burned) < MAX_UTILIZATION:
        network.tick(parties)

        def get_move_status(p_id):
            """
            Returns:
            'data' if next pad is fresh and gap is safe.
            'drift' if next pad is burned but gap is safe.
            None if gap is unsafe (blocked by neighbor).
            """
            p = parties[p_id]
            front_id = (p.party_id % m) + 1
            neighbor_pos = p.view_of_others[front_id]

            gap = (neighbor_pos - p.my_index) % n
            next_idx = (p.my_index + 1) % n

            if gap > d:
                if next_idx not in burned:
                    return 'data', next_idx
                else:
                    return 'drift', next_idx
            return None, None

        moved_in_tick = False

        # 1. Priority: Active senders
        # They either encrypt (burn) or drift (skip burned pads)
        legal_senders = [pid for pid in active_ids if get_move_status(pid)[0] is not None]
        if legal_senders:
            sid = random.choice(legal_senders)
            status, nxt = get_move_status(sid)

            parties[sid].my_index = nxt
            if status == 'data':
                if nxt in burned:
                    # This is a 'Loud Fail' - it proves a security breach occurred
                    raise RuntimeError(f"CRITICAL SECURITY FAILURE: Pad index {nxt} reused!")
                burned.add(nxt)
                parties[sid].pads_used += 1

            # Broadcast the new position regardless of whether it was data or drift
            network.send_broadcast(sid, nxt)
            moved_in_tick = True

        # 2. Priority: Silent parties (Always jump/drift, never burn)
        else:
            legal_jumpers = [pid for pid in silent_ids if get_move_status(pid)[0] is not None]
            if legal_jumpers:
                jid = random.choice(legal_jumpers)
                status, nxt = get_move_status(jid)
                parties[jid].my_index = nxt
                network.send_broadcast(jid, nxt)
                moved_in_tick = True

        # Termination: Break if no one can move and no broadcasts are pending
        if not moved_in_tick and not network.queue:
            break

    return n - len(burned)


if __name__ == "__main__":
    for M in [3, 4]:
        N, D = 2000, 15
        TRIALS = 50
        print(f"\n--- Cooperative Ring Simulation (M={M}, N={N}, D={D}) ---")
        print(f"{'Scenario (S.x)':<15} | {'Avg Wasted Pads':<15} | {'Utilization %':<10}")
        print("-" * 55)

        for x in range(1, M + 1):
            results = [run_scenario(N, M, D, x) for _ in range(TRIALS)]
            avg_waste = statistics.mean(results)
            utilization = ((N - avg_waste) / N) * 100
            print(f"S.{x:<13} | {avg_waste:<15.2f} | {utilization:<10.2f}%")