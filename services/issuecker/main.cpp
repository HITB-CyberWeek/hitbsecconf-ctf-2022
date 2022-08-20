#include "api.h"
#include <utility>
#include <iostream>

#include <cgicc/Cgicc.h>
#include <cgicc/HTTPHTMLHeader.h>

using namespace cgicc;

int main(int argc, char **argv) {
    RedisConfig redis_config{"localhost:6379", ""};
    api api(redis_config);

    std::string username = "username";
    std::string password = "password";
//    api.register_user(username, password);

    std::cout << api.validate_password("usern1ame", "");

    Cgicc cgi;


    // Send HTTP header
    std::cout << HTTPContentHeader("Content-Type: application/json") << std::endl;
    std::cout << R"({"data": ")" << cgi.getEnvironment().getPostData() << "\"}";
    return 0;
}
