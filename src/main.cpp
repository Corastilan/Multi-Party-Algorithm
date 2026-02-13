#include "directional_protocol.h"
#include <iostream>

void runScenario1(DirectionalProtocol& protocol) {
    std::cout << "\n========================================\n";
    std::cout << "SCENARIO 1: Sequential sends from each party\n";
    std::cout << "========================================\n";

    protocol.printState();

    EncryptedMessage encrypted;

    // Party sending
    if (protocol.sendMessage(Party::ALICE, "Hello from Alice!", encrypted)) {
        std::string decrypted = protocol.receiveMessage(encrypted);
        std::cout << "  Decrypted: \"" << decrypted << "\"\n";
    }

    if (protocol.sendMessage(Party::BOB, "Greetings from Bob!", encrypted)) {
        std::string decrypted = protocol.receiveMessage(encrypted);
        std::cout << "  Decrypted: \"" << decrypted << "\"\n";
    }

    if (protocol.sendMessage(Party::CHARLIE, "Hi from Charlie!", encrypted)) {
        std::string decrypted = protocol.receiveMessage(encrypted);
        std::cout << "  Decrypted: \"" << decrypted << "\"\n";
    }

    protocol.printState();
}

void runScenario2(DirectionalProtocol& protocol) {
    std::cout << "\n========================================\n";
    std::cout << "SCENARIO 2: Multiple sends to test gap constraint\n";
    std::cout << "========================================\n";

    protocol.printState();

    EncryptedMessage encrypted;

    std::cout << "\n--- Alice sends 3 messages ---\n";
    for (int i = 1; i <= 3; ++i) {
        std::string msg = "Alice message #" + std::to_string(i);
        protocol.sendMessage(Party::ALICE, msg, encrypted);
    }

    // alternating direction
    std::cout << "\n--- Charlie sends 3 messages ---\n";
    for (int i = 1; i <= 3; ++i) {
        std::string msg = "Charlie message #" + std::to_string(i);
        protocol.sendMessage(Party::CHARLIE, msg, encrypted);
    }

    std::cout << "\n--- Bob sends 2 messages ---\n";
    for (int i = 1; i <= 2; ++i) {
        std::string msg = "Bob message #" + std::to_string(i);
        protocol.sendMessage(Party::BOB, msg, encrypted);
    }

    protocol.printState();
}

void runScenario3(DirectionalProtocol& protocol) {
    std::cout << "\n========================================\n";
    std::cout << "SCENARIO 3: Testing gap constraint violation\n";
    std::cout << "========================================\n";

    protocol.printState();

    EncryptedMessage encrypted;

    // Testing rapid messages
    std::cout << "\n--- Alice attempts to send many messages ---\n";
    for (int i = 1; i <= 15; ++i) {
        std::string msg = "Rapid message #" + std::to_string(i);
        bool success = protocol.sendMessage(Party::ALICE, msg, encrypted);
        if (!success) {
            std::cout << "  Alice blocked after " << (i-1) << " messages due to gap constraint.\n";
            break;
        }
    }

    protocol.printState();

    std::cout << "\n--- Bob sends to free up gap ---\n";
    protocol.sendMessage(Party::BOB, "Bob helps clear the gap", encrypted);

    protocol.printState();

    std::cout << "\n--- Alice tries again ---\n";
    protocol.sendMessage(Party::ALICE, "Alice can send again!", encrypted);

    protocol.printState();
}

int main() {
    std::cout << "Multi-Party Secure Communication Protocol\n";
    std::cout << "Directional Assignment with Gap Constraints\n";
    std::cout << "==========================================\n\n";

    // Modify as needed. 100 pads works best and d = 5.
    const int TOTAL_PADS = 100;
    const int MAX_UNDELIVERED = 5;

    std::cout << "Configuration:\n";
    std::cout << "  Total pads (n): " << TOTAL_PADS << "\n";
    std::cout << "  Max undelivered messages (d): " << MAX_UNDELIVERED << "\n\n";

    DirectionalProtocol protocol(TOTAL_PADS, MAX_UNDELIVERED);
    protocol.generatePads();

    // testing
    runScenario1(protocol);

    DirectionalProtocol protocol2(TOTAL_PADS, MAX_UNDELIVERED);
    protocol2.generatePads();
    runScenario2(protocol2);

    DirectionalProtocol protocol3(TOTAL_PADS, MAX_UNDELIVERED);
    protocol3.generatePads();
    runScenario3(protocol3);

    std::cout << "\n========================================\n";
    std::cout << "All scenarios completed!\n";
    std::cout << "========================================\n";

    return 0;
}
