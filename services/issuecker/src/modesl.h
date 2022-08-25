#ifndef ISSUECKER_MODESL_H
#define ISSUECKER_MODESL_H
#include <string>


struct Queue {
    std::string name;
    std::string key;
    std::string owner;
};


struct Ticket {
    std::string title;
    std::string description;
};


struct RedisConfig {
    std::string address;
    std::string password;
};


#endif //ISSUECKER_MODESL_H
