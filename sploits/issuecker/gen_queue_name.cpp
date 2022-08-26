#include <iostream>
#include <sstream>
#include <random>

static const std::string ALPHA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";


std::string gen_random_string(uint length) {
    std::random_device random_device;
    std::mt19937 generator(random_device());
    std::uniform_int_distribution<> distribution(0, ALPHA.size() - 1);

    std::stringstream random_string;

    for (uint i = 0; i < length; ++i) {
        random_string << ALPHA[distribution(generator)];
    }
    return random_string.str();
}


double get_queue_hash(std::string_view name) {
    auto res = name[0] * pow(2, 0);

    for (int i = 0; i < name.length(); ++i) {
        res += ((uint)(name[i] * pow(2, (i % 10))) % (uint)(i % 100 + 1)) * 1749;
    }
    return res;
}


int main() {
    while (true) {
        auto queue_name = gen_random_string(40);
        if (get_queue_hash(queue_name) > 1000000) {
            std::cout << queue_name << std::endl;
            return 0;
        }
    }
}

