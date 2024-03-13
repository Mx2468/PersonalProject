#include <iostream>
#include <cmath>

const int size = 10000;
const int numIterations = 100000;

int main() {
    double data[size];

    // Initialize data
    for (int i = 0; i < size; ++i) {
        data[i] = i * 0.1;
    }

    // Perform some computation multiple times
    double result = 0.0;
    for (int iteration = 0; iteration < numIterations; ++iteration) {
        for (int i = 0; i < size; ++i) {
            result += std::sin(data[i]);
        }
    }

    // Print the result to prevent optimizations removing the computation
    std::cout << result << std::endl;

    return 0;
}