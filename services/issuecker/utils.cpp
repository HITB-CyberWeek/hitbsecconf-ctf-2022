#include <cmath>
#include <sstream>
#include <iostream>
#include <boost/beast/core/detail/base64.hpp>
#include "utils.h"


std::string get_queue_hash(std::string_view name) {
    auto res = name[0] * pow(10, 0);

    for (int i = 0; i < name.length(); ++i) {
        res += name[i] * pow(10, i);
    }
    std::stringstream ss;
    ss << res;
    return ss.str();
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
