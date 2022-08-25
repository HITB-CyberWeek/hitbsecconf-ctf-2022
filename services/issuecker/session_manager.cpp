#include <random>
#include <boost/compute/detail/sha1.hpp>
#include "session_manager.h"
#include "utils.h"

SessionManager::SessionManager(const RedisConfig &redis_config) {
    redis_client.SetRedisConfig(redis_config.address, redis_config.password);
    redis_client.SetRedisReadWriteType(FlyRedisReadWriteType::ReadOnSlaveWriteOnMaster);
    redis_client.Open();
}

std::string SessionManager::create_session(const std::string &username) {
    auto salt = gen_random_string(32);
    std::string secret = boost::compute::detail::sha1(username + salt);
    int res;
    redis_client.HSET("salts", username, salt, res);
    return secret;
}

void SessionManager::delete_session(const std::string &username) {
    int res;
    redis_client.HDEL("salts", username, res);
}

bool SessionManager::validate_session(const std::string &username, const std::string& secret) {
    std::string salt;
    redis_client.HGET("salts", username, salt);
    if (salt.empty()) {
        return false;
    }

    std::string expected_secret = boost::compute::detail::sha1(username + salt);
    return expected_secret == secret;
}
