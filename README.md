# Cooperative Global Ring: Asynchronous OTP Simulation

This project implements a **Distributed One-Time Pad (OTP)** protocol designed for a circular buffer (Ring) of cryptographic material. The simulation demonstrates how multiple parties can securely share a finite sequence of random pads in an asynchronous network environment.

## 🚀 How to Test

### Prerequisites
* **Python 3.8+**
* No external dependencies (uses standard `random` and `statistics` libraries).

### Execution
1. Save the provided script as `ring_sim.py`.
2. Run the script via your terminal or IDE:
   ```bash
   python ring_sim.py
   ```
3. The script will iterate through two configurations ($M=3$ and $M=4$ parties) and test every possible number of active senders ($x$).

### Interpreting Results
* **S.x**: The scenario where $x$ parties are actively trying to send data.
* **Avg Wasted Pads**: The count of pads remaining in the ring that were never used for encryption when the system reached a deadlock.
* **Utilization %**: The efficiency of the protocol. With $N=2000$ and $D=15$, you should see utilization stay consistently high (~97%) across all scenarios.

---

## 🛠 Functionalities

### 1. Asynchronous Network Simulation
The `AsynchronousNetwork` class simulates real-world network jitter. 
* **Broadcast Latency**: Messages (position updates) are delayed by a random factor ($0$ to $D$ ticks).
* **Stale Information**: Parties must make movement decisions based on their `view_of_others`, which represents where they *think* their neighbors are, not where they actually are.

### 2. The Cooperative "Drift"
This is the core innovation of the protocol. It allows the ring to rotate even when only one person is talking:
* **Passive Traversal**: If a party encounters a pad already used by someone else, they "drift" (advance their pointer) without consuming new material.
* **Yielding Territory**: Silent parties jump forward to maintain the safety buffer, effectively yielding the rest of the ring to active senders.

### 3. Collision Avoidance
The protocol enforces a **Safety Invariant ($D$)**. No party will move within $D$ pads of a neighbor's last known position. This $D$ buffer acts as a "crumple zone" that absorbs network latency, preventing two parties from ever landing on the same pad index.

---

## 💻 Code Walkthrough

### 1. Setup & Initialization
The ring is initialized with $N$ pads. Parties are placed at equal intervals (e.g., $0, 500, 1000, 1500$). 
* **`active_ids`**: Parties assigned to send data.
* **`burned`**: A global set tracking which indices have been used for XOR encryption.

### 2. The Decision Engine: `get_move_status`
Every tick, each party evaluates the pad immediately in front of them ($Index + 1$):
* **Gap Check**: Is $(Neighbor\_Pos - My\_Pos) \pmod N > D$?
* **Status Assignment**: 
    * If the gap is safe and the pad is fresh $\rightarrow$ `data` (Ready to encrypt).
    * If the gap is safe but the pad is used $\rightarrow$ `drift` (Ready to skip).
    * If the gap is unsafe $\rightarrow$ `None` (Must wait).



### 3. The Execution Loop
The `while` loop processes moves based on priority:
1. **Active Senders**: Attempt to move. If the status is `data`, they increment `pads_used` and add the index to the `burned` set.
2. **Silent Jumpers**: If active senders are blocked, silent parties move to clear the path. They only ever "drift."
3. **Broadcast**: Any move triggers `network.send_broadcast`, which eventually updates the `view_of_others` for all other parties after a delay.



### 4. Termination (The Clinch)
The simulation stops when no party can move and the network queue is empty.
* **S.1 (Solo)**: The sender "pushes" everyone else until they are bunched up, leaving only $M$ x $D$-sized gap.
* **S.4 (Full)**: All parties are spaced out by exactly $D$ pads.



---

## 🛡 Security Analysis

### Perfect Secrecy
By checking `next_idx not in burned` before every `data` move, the protocol guarantees that no cryptographic pad is ever used twice. This preserves the core requirement of the One-Time Pad.

### Race Condition Protection
Because the safety gap $D$ is equal to the maximum network delay, it is mathematically impossible for a party to "catch up" to a neighbor before receiving that neighbor's most recent position broadcast. This ensures **Mutual Exclusion** over the pad indices.
