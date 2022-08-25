#include <cmath>
#include <sstream>
#include <iostream>
#include <fstream>
#include <random>
#include <boost/beast/core/detail/base64.hpp>
#include "utils.h"


std::string get_queue_hash(std::string_view name) {
    auto res = name[0] * pow(2, 0);

    for (int i = 0; i < name.length(); ++i) {
        res += ((uint)(name[i] * pow(2, (i % 10))) % (uint)(i % 100 + 1)) * 1749;
    }
    std::stringstream ss;
    ss << res;
    return ss.str();
}


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

std::string base64encode(const std::string& source) {
    auto size = boost::beast::detail::base64::encoded_size(source.length());
    char* res = new char[size];
    auto new_size = boost::beast::detail::base64::encode(res, source.c_str(), source.length());
    std::string string_res(res, new_size);
    delete[] res;
    return string_res;
}


std::string base64decode(const std::string& source) {
    auto size = boost::beast::detail::base64::decoded_size(source.length());
    char* res = new char[size];
    auto [new_size, inp_read] = boost::beast::detail::base64::decode(res, source.c_str(), source.length());
    std::string string_res(res, new_size);
    delete[] res;
    return string_res;
}


void log(const std::string& message)  {
    std::ofstream outfile;
    outfile.open(LOG_FILE, std::ios_base::app);

    time_t     now = time(nullptr);
    char       buf[80];
    auto tstruct = *localtime(&now);
    strftime(buf, sizeof(buf), "%Y-%m-%d.%X", &tstruct);

    std::string sbuf = buf;
    outfile << getpid() << ": " << sbuf << " " << message << std::endl;
}
