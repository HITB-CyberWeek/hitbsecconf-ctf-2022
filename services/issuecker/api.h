#ifndef ISSUECKER_API_H
#define ISSUECKER_API_H
#include <string>
#include <unordered_map>
#include <boost/beast/core/detail/base64.hpp>
#include <boost/compute/detail/sha1.hpp>
#include "fly_redis.h"
#include "modesl.h"
#include "session_manager.h"

using csl = const std::string&;

class DumpedQuery {
    static const int DUMP_SIZE = 300;

public:
    void set_queue_id(const std::string& queue_id) ;

    void set_ticket_id(const std::string& ticket_id) ;

    void set_title(const std::string& title) ;

    void set_description(const std::string& description) ;

    std::string dump() ;

private:
    void add_field(const std::string& fld_value, unsigned long& fld_len);
    unsigned long offset = 0;
    unsigned long queue_id_len{};
    unsigned long ticket_id_len{};
    unsigned long title_len{};
    unsigned long description_len{};
    char composed_query[DUMP_SIZE]{};
};

int get_ticket_sub_id(const std::string& ticket_id);

std::string dump_ticket(const std::string& title, const std::string& description);

Ticket load_ticket(const std::string& dumped_ticket);

class Api {
public:
    explicit Api(const RedisConfig& redis_config);
    std::vector<Queue> queues;
    std::vector<std::unordered_map<std::string, Ticket>> queue_id_to_tickets;

    std::pair<long long, std::string> add_queue(std::string& name, const std::string& owner);

    Queue get_queue(unsigned long queue_id);

    std::string add_ticket(unsigned long queue_id, std::string &title, std::string &description);

    std::vector<Ticket> find_tickets(unsigned long queue_id, const std::string& ticket_id, const std::string& title, const std::string& description);

    bool is_user_exists(csl username);

    void register_user(csl username, csl password);

    bool validate_password(csl username, csl password);

    CFlyRedisClient redis_client;
    SessionManager sm;
};


bool is_ticket_correct(Queue& queue, std::string& ticket_id);

bool is_title_correct(std::string& title);

bool is_description_correct(std::string& title);

#endif //ISSUECKER_API_H
