#ifndef ISSUECKER_SESSION_MANAGER_H
#define ISSUECKER_SESSION_MANAGER_H
#include "modesl.h"
#include "fly_redis.h"

class SessionManager {
public:
    explicit SessionManager(const RedisConfig& redis_config);

    std::string create_session(const std::string& username);

    void delete_session(const std::string& username);

    bool validate_session(const std::string& username, const std::string& secret);
private:
    CFlyRedisClient redis_client;
};


#endif //ISSUECKER_SESSION_MANAGER_H
