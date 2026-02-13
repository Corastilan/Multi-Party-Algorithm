#include "protocol_state.h"
#include <algorithm>
#include <cmath>

ProtocolState::ProtocolState(int totalPads, int maxUndelivered)
    : n(totalPads), d(maxUndelivered), charlieDirection(1) {

    // Initialize last used indices according to the algorithm
    lastUsed[Party::ALICE] = 0;                    // Alice starts at 1 (0 + 1)
    lastUsed[Party::BOB] = n + 1;                  // Bob starts at n (n+1 - 1)
    lastUsed[Party::CHARLIE] = static_cast<int>(std::floor(n / 2.0));  // Charlie at middle
}

int ProtocolState::getLastUsed(Party p) const {
    std::lock_guard<std::mutex> lock(stateMutex);
    auto it = lastUsed.find(p);
    if (it != lastUsed.end()) {
        return it->second;
    }
    return -1;
}

void ProtocolState::setLastUsed(Party p, int index) {
    std::lock_guard<std::mutex> lock(stateMutex);
    lastUsed[p] = index;
}

int ProtocolState::getCharlieDirection() const {
    std::lock_guard<std::mutex> lock(stateMutex);
    return charlieDirection;
}

void ProtocolState::flipCharlieDirection() {
    std::lock_guard<std::mutex> lock(stateMutex);
    charlieDirection = -charlieDirection;
}

bool ProtocolState::checkGapConstraint(Party sender, int nextPad) const {
    std::lock_guard<std::mutex> lock(stateMutex);

    int minGap = n + 1;

    for (const auto& pair : lastUsed) {
        if (pair.first != sender) {
            int gap = std::abs(nextPad - pair.second);
            minGap = std::min(minGap, gap);
        }
    }

    return minGap > d;
}
