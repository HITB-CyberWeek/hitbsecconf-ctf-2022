#include <cmath>
#include <sstream>
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
    auto size = boost::beast::detail::base64::encoded_size(source.size());
    char* res = new char[size];
    boost::beast::detail::base64::encode(res, source.data(), size);
    return {res};
}


std::string base64decode(const std::string& source) {
    auto size = boost::beast::detail::base64::decoded_size(source.size());
    char* res = new char[size];
    boost::beast::detail::base64::decode(res, source.data(), size);
    return {res};
}
