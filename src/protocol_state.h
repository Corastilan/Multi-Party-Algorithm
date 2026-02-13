#ifndef PROTOCOL_STATE_H
#define PROTOCOL_STATE_H

#include "types.h"
#include <map>
#include <mutex>

class ProtocolState {
private:
    int n;  // Total number of pads
    int d;  // Maximum undelivered messages constraint

    // Shared state: last used pad index for each party
    std::map<Party, int> lastUsed;

    // Charlie's direction for alternating variant
    int charlieDirection;

        mutable std::mutex stateMutex;

public:
    ProtocolState(int totalPads, int maxUndelivered);

    int getLastUsed(Party p) const;

    void setLastUsed(Party p, int index);

    int getCharlieDirection() const;

    void flipCharlieDirection();

    int getTotalPads() const { return n; }
    int getMaxUndelivered() const { return d; }

    bool checkGapConstraint(Party sender, int nextPad) const;
};

#endif // PROTOCOL_STATE_H
