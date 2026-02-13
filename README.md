# Simple test

This is a C++ implementation of Algorithm 1 from the PDF. This is a simple test as to what it looks like. Note that I use C++ for practice. 
The final algorithm will be constructed in Python. This is just an overview.

## Overview

The protocol enables three parties (Alice, Bob, and Charlie) to send encrypted messages using one-time pads while:
- Ensuring perfect secrecy (each pad used exactly once)
- Maintaining a gap constraint to prevent collision
- Minimizing wasted pads through directional assignment

## Architecture

The implementation is modularized into several components:

### Core Modules

1. **types.h** - Common type definitions
 
2. **protocol_state.h/cpp** - State management
 
3. **directional_protocol.h/cpp** - Main protocol logic

4. **main.cpp** - Main program

## Protocol Design

### Party Assignments
- **Alice**: Uses pads from index 1, incrementing (1, 2, 3, ...)
- **Bob**: Uses pads from index n, decrementing (n, n-1, n-2, ...)
- **Charlie**: Starts at ⌊n/2⌋, alternates direction (+1, -1, +1, -1, ...)

### Gap Constraint
A party P can only use their next pad if:
```
min_{Q ≠ P} |next_pad(P) - last_used_pad(Q)| > d
```
where d is the maximum number of undelivered messages in the network.

## Building and Running

### Prerequisites
- C++17 compatible compiler 
- Make (optional, for using Makefile)

### Compilation

Using Make:
```bash
make
```
To remove object files, simply run:
```bash
make clean
```

### Running

```bash
./directional_protocol
```

Or using Make:
```bash
make run
```

## Example Output

The program runs three test scenarios:

1. **Sequential sends** - Each party sends one message
2. **Multiple sends** - Tests gap constraint with multiple messages
3. **Gap violation** - Demonstrates constraint enforcement

Sample output:
```
=== Protocol State ===
Total pads: 100
Max undelivered (d): 5
Last used pads:
  Alice:   0
  Bob:     101
  Charlie: 50 (direction: +)
======================

Alice successfully sent message using pad 1
  Decrypted: "Hello from Alice!"
```

## Configuration

Key parameters can be adjusted in `main.cpp`:
- `TOTAL_PADS` (n) - Total number of one-time pads available
- `MAX_UNDELIVERED` (d) - Maximum undelivered messages constraint

## Performance Analysis

From the PDF analysis:
- **Best case waste**: ~d pads (when all parties send equally)
- **Worst case waste**: ~2n/3 pads (when only one party sends)
- **Time complexity**: O(1) per message send operation

## Thread Safety

The `ProtocolState` class uses mutex locks to ensure thread-safe access to shared state, making the implementation suitable for concurrent environments.

## Limitations

- This implementation uses simplified XOR encryption for demonstration
- In production, secure key management and storage would be required
- The pad generation uses pseudo-random numbers (not cryptographically secure)

## Future Enhancements

Possible improvements:
- Implement Idea 2 (Round-Robin) and Idea 3 (Adaptive Boundaries)
- Add network simulation for message delivery
- Implement proper cryptographic pad generation
- Add metrics collection for waste analysis
- Support for more than 3 parties
