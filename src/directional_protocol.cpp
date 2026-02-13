#include "directional_protocol.h"
#include <iostream>
#include <random>

DirectionalProtocol::DirectionalProtocol(int totalPads, int maxUndelivered) {
    state = std::make_shared<ProtocolState>(totalPads, maxUndelivered);
}

void DirectionalProtocol::generatePads() {
    int n = state->getTotalPads();
    pads.resize(n + 2);  // Extra space for boundary indices

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 255);

    // Generate random pads of length 1024 bytes each
    for (int i = 0; i <= n + 1; ++i) {
        pads[i].resize(1024);
        for (auto& byte : pads[i]) {
            byte = static_cast<uint8_t>(dis(gen));
        }
    }
}

int DirectionalProtocol::computeNextPad(Party p) const {
    switch(p) {
        case Party::ALICE:
            // Alice increments from 1
            return state->getLastUsed(Party::ALICE) + 1;

        case Party::BOB:
            // Bob decrements from n
            return state->getLastUsed(Party::BOB) - 1;

        case Party::CHARLIE:
            // Charlie alternates direction from middle
            return state->getLastUsed(Party::CHARLIE) + state->getCharlieDirection();

        default:
            return -1;
    }
}

std::vector<uint8_t> DirectionalProtocol::encryptMessage(
    const std::string& message, int padIndex) const {

    const auto& pad = pads[padIndex];
    std::vector<uint8_t> ciphertext;
    ciphertext.reserve(message.size());

    // Simple XOR encryption
    for (size_t i = 0; i < message.size(); ++i) {
        uint8_t plainByte = static_cast<uint8_t>(message[i]);
        uint8_t padByte = pad[i % pad.size()];
        ciphertext.push_back(plainByte ^ padByte);
    }

    return ciphertext;
}

std::string DirectionalProtocol::decryptMessage(
    const std::vector<uint8_t>& ciphertext, int padIndex) const {

    const auto& pad = pads[padIndex];
    std::string plaintext;
    plaintext.reserve(ciphertext.size());

    // XOR decryption (same as encryption for one-time pad)
    for (size_t i = 0; i < ciphertext.size(); ++i) {
        uint8_t cipherByte = ciphertext[i];
        uint8_t padByte = pad[i % pad.size()];
        plaintext.push_back(static_cast<char>(cipherByte ^ padByte));
    }

    return plaintext;
}

bool DirectionalProtocol::sendMessage(
    Party sender, const std::string& message, EncryptedMessage& outEncrypted) {

    // Step 1: Compute next pad index for this party
    int nextPad = computeNextPad(sender);

    // Step 2: Check if next pad is within valid range
    int n = state->getTotalPads();
    if (nextPad < 1 || nextPad > n) {
        std::cout << partyToString(sender) << " has exhausted their pad range.\n";
        return false;
    }

    // Step 3: Check gap constraint with all other parties
    if (!state->checkGapConstraint(sender, nextPad)) {
        std::cout << partyToString(sender) << " cannot send - gap constraint violated "
                  << "(next pad: " << nextPad << ", max gap: " << state->getMaxUndelivered() << ")\n";
        return false;
    }

    // Step 4: Encrypt the message
    outEncrypted.ciphertext = encryptMessage(message, nextPad);
    outEncrypted.sender = sender;
    outEncrypted.padIndex = nextPad;

    // Step 5: Update state
    state->setLastUsed(sender, nextPad);

    // Step 6: If Charlie, flip direction for alternating variant
    if (sender == Party::CHARLIE) {
        state->flipCharlieDirection();
    }

    std::cout << partyToString(sender) << " successfully sent message using pad "
              << nextPad << "\n";

    return true;
}

std::string DirectionalProtocol::receiveMessage(const EncryptedMessage& encrypted) const {
    return decryptMessage(encrypted.ciphertext, encrypted.padIndex);
}

void DirectionalProtocol::printState() const {
    std::cout << "\n=== Protocol State ===\n";
    std::cout << "Total pads: " << state->getTotalPads() << "\n";
    std::cout << "Max undelivered (d): " << state->getMaxUndelivered() << "\n";
    std::cout << "Last used pads:\n";
    std::cout << "  Alice:   " << state->getLastUsed(Party::ALICE) << "\n";
    std::cout << "  Bob:     " << state->getLastUsed(Party::BOB) << "\n";
    std::cout << "  Charlie: " << state->getLastUsed(Party::CHARLIE)
              << " (direction: " << (state->getCharlieDirection() > 0 ? "+" : "-") << ")\n";
    std::cout << "======================\n\n";
}
