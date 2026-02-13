#ifndef TYPES_H
#define TYPES_H

#include <string>
#include <vector>
#include <cstdint>

enum class Party {
    ALICE,
    BOB,
    CHARLIE
};

inline std::string partyToString(Party p) {
    switch(p) {
        case Party::ALICE: return "Alice";
        case Party::BOB: return "Bob";
        case Party::CHARLIE: return "Charlie";
        default: return "Unknown";
    }
}

struct Message {
    std::string content;
    Party sender;
    std::vector<Party> recipients;
};

struct EncryptedMessage {
    std::vector<uint8_t> ciphertext;
    Party sender;
    int padIndex;
};

#endif // TYPES_H
