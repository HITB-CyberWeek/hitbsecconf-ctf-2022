#include <random>
#include <boost/compute/detail/sha1.hpp>
#include "session_manager.h"
#include "utils.h"

SessionManager::SessionManager(const RedisConfig &redis_config) {
    redis_client.SetRedisConfig(redis_config.address, redis_config.password);
    redis_client.SetRedisReadWriteType(FlyRedisReadWriteType::ReadOnSlaveWriteOnMaster);
    redis_client.Open();
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
