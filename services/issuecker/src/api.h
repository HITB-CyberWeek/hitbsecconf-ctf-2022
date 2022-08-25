#ifndef ISSUECKER_API_H
#define ISSUECKER_API_H
#include <string>
#include <unordered_map>
#include <boost/beast/core/detail/base64.hpp>
#include <boost/compute/detail/sha1.hpp>
#include "fly_redis.h"
#include "modesl.h"
#include "session_manager.h"


int get_ticket_sub_id(const std::string& ticket_id);

std::string dump_ticket(const std::string& title, const std::string& description);

Ticket load_ticket(const std::string& dumped_ticket);

class Api {
public:
    explicit Api(const RedisConfig& redis_config);
    std::unordered_map<std::string, std::vector<Ticket>> cache;

    std::pair<long long, std::string> add_queue(std::string& name, const std::string& owner);

    Queue get_queue(unsigned long queue_id);

    std::string add_ticket(unsigned long queue_id, std::string &title, std::string &description);

    std::vector<Ticket> find_tickets(unsigned long queue_id, const std::string& ticket_id, const std::string& title, const std::string& description);

    bool is_user_exists(const std::string& username);

    void register_user(const std::string& username, const std::string& password);

    bool validate_password(const std::string& username, const std::string& password);

    CFlyRedisClient redis_client;
    SessionManager sm;
};


bool is_ticket_correct(Queue& queue, const std::string& ticket_id);

#endif //ISSUECKER_API_H
