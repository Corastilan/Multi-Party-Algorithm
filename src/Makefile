CXX = g++
CXXFLAGS = -std=c++20 -Wall -Wextra -O2
TARGET = directional_protocol
SOURCES = main.cpp protocol_state.cpp directional_protocol.cpp
OBJECTS = $(SOURCES:.cpp=.o)
HEADERS = types.h protocol_state.h directional_protocol.h

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJECTS)

%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)

run: $(TARGET)
	./$(TARGET)

rebuild: clean all

.PHONY: all clean run rebuild
