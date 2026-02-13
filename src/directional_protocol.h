#ifndef DIRECTIONAL_PROTOCOL_H
#define DIRECTIONAL_PROTOCOL_H

#include "types.h"
#include "protocol_state.h"
#include <memory>
#include <vector>

class DirectionalProtocol {
private:
    std::shared_ptr<ProtocolState> state;

    // One-time pad storage
    std::vector<std::vector<uint8_t>> pads;

    // Compute the next pad index for a given pad
    int computeNextPad(Party p) const;

    // Simple XOR encryption with one-time pad
    std::vector<uint8_t> encryptMessage(const std::string& message, int padIndex) const;

    // Simple XOR decryption with one-time pad
    std::string decryptMessage(const std::vector<uint8_t>& ciphertext, int padIndex) const;

public:
    DirectionalProtocol(int totalPads, int maxUndelivered);

    void generatePads();

    bool sendMessage(Party sender, const std::string& message, EncryptedMessage& outEncrypted);

    std::string receiveMessage(const EncryptedMessage& encrypted) const;

     void printState() const;
};

#endif // DIRECTIONAL_PROTOCOL_H
