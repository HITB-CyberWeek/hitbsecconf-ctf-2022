#ifndef ISSUECKER_API_H
#define ISSUECKER_API_H
#include <string>
#include <unordered_map>
#include <boost/beast/core/detail/base64.hpp>
#include <boost/compute/detail/sha1.hpp>
#include "fly_redis.h"


using csl = const std::string&;


struct Queue {
    std::string name;
    std::string key;
};


struct Ticket {
    std::string title;
    std::string description;
};


struct RedisConfig {
    std::string address;
    std::string password;
};

std::string base64encode(const std::string& source);

std::string base64decode(const std::string& source);

std::string get_queue_hash(std::string_view name);

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

class api {
public:
    explicit api(const RedisConfig& redis_config) {
        redis_client.SetRedisConfig(redis_config.address, redis_config.password);
        redis_client.SetRedisReadWriteType(FlyRedisReadWriteType::ReadOnSlaveWriteOnMaster);
        redis_client.Open();
    }
    std::vector<Queue> queues;
    std::vector<std::unordered_map<std::string, Ticket>> queue_id_to_tickets;

    std::pair<long long, std::string> add_queue(std::string& name) {
        auto queue_hash = get_queue_hash(name);

        std::stringstream ss;
        ss << base64encode(name) << ":" << queue_hash;
        std::string q = ss.str();

        int queue_count;
        redis_client.RPUSH("queues", ss.str(), queue_count);
        return std::make_pair(queue_count - 1, queue_hash);
    }

    Queue get_queue(unsigned long queue_id) {
        std::vector<std::string> queues_res;
        redis_client.LRANGE("queues", (int)queue_id, (int)queue_id, queues_res);
        if (queues_res.empty()) {
            std::stringstream ss;
            ss << "invalid queue id: " << queue_id;
            throw std::runtime_error(ss.str());
        }

        auto pos = queues_res[0].find(':');
        Queue res;
        res.name = base64decode(queues_res[0].substr(0, pos));
        res.key = queues_res[0].substr(pos + 1, queues_res[0].size());
        return res;
    }

    std::string add_ticket(long long queue_id, std::string& title, std::string& description) {
        std::lock_guard _(mtx);

        auto queue = get_queue(queue_id);
        std::stringstream queue_to_tickets_key;
        queue_to_tickets_key << "queues/" << queue_id;

        int ticket_count;
        redis_client.LLEN(queue_to_tickets_key.str(), ticket_count);
        auto ticket_id = queue.key + "-" + std::to_string(ticket_count);

        std::string dumped_ticket = dump_ticket(title, description);
        redis_client.RPUSH(queue_to_tickets_key.str(), dumped_ticket, ticket_count);

        return ticket_id;
    }

    std::vector<Ticket> find_tickets(unsigned long queue_id, const std::string& ticket_id, const std::string& title, const std::string& description) {
        DumpedQuery dumped_q;
        dumped_q.set_queue_id(std::to_string(queue_id));
        if (!ticket_id.empty()) {
            dumped_q.set_ticket_id(ticket_id);
        }
        if (!title.empty()) {
            dumped_q.set_title(title);
        }
        if (!description.empty()) {
            dumped_q.set_description(description);
        }
        auto queue = get_queue(queue_id);

        if (!ticket_id.empty()) {
            int ticket_sub_id = get_ticket_sub_id(ticket_id);
            std::stringstream queue_to_tickets_key;
            queue_to_tickets_key << "queues/" << queue_id;

            std::vector<std::string> res;
            redis_client.LRANGE(queue_to_tickets_key.str(), ticket_sub_id, ticket_sub_id, res);

            std::vector<Ticket> ticket_res;
            for (auto &dumped_ticket: res) {
                ticket_res.push_back(load_ticket(dumped_ticket));
            }
            return ticket_res;
        }
        throw std::runtime_error("not implemented");
    }

    bool is_user_exists(csl username) ;

    void register_user(csl username, csl password) ;

    bool validate_password(csl username, csl password);

    std::mutex mtx;
    CFlyRedisClient redis_client;
};


bool is_ticket_correct(Queue& queue, std::string& ticket_id);

bool is_title_correct(std::string& title);

bool is_description_correct(std::string& title);

#endif //ISSUECKER_API_H
