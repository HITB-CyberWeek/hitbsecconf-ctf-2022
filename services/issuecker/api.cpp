#include <regex>
#include <iostream>
#include "api.h"
#include "utils.h"
#include "hasher.h"


std::string dump_ticket(const std::string& title, const std::string& description) {
    return base64encode(title) + ":" + base64encode(description);
}

Ticket load_ticket(const std::string& dumped_ticket) {
    auto pos = dumped_ticket.find(':');
    auto part_one = dumped_ticket.substr(0, pos);
    auto part_two = dumped_ticket.substr(pos + 1, dumped_ticket.length());
    return {base64decode(part_one), base64decode(part_two)};
}


int get_ticket_sub_id(const std::string& ticket_id) {
    auto pos = ticket_id.find('-');
    return std::stoi(ticket_id.substr(pos + 1, ticket_id.size()));
}


bool Api::validate_password(const std::string &username, const std::string &password) {
    std::string expected_hash;
    redis_client.HGET("p_hashes", username, expected_hash);
    std::string real_hash = boost::compute::detail::sha1(password);
    return expected_hash == real_hash;
}

void Api::register_user(const std::string &username, const std::string &password) {
    std::string p_hash = boost::compute::detail::sha1(password);
    int res;
    redis_client.HSET("p_hashes", username, p_hash, res);
}

bool Api::is_user_exists(const std::string &username) {
    int exists;
    redis_client.HEXISTS("p_hashes", username, exists);
    return (bool)exists;
}

Api::Api(const RedisConfig &redis_config)
    : sm(redis_config)
{
    redis_client.SetRedisConfig(redis_config.address, redis_config.password);
    redis_client.SetRedisReadWriteType(FlyRedisReadWriteType::ReadOnSlaveWriteOnMaster);
    redis_client.Open();
}

std::pair<long long, std::string> Api::add_queue(std::string &name, const std::string& owner)  {
    auto queue_hash = get_queue_hash(name);

    std::stringstream ss;
    ss << base64encode(name) << ":" << queue_hash << ":" << owner;
    std::string q = ss.str();

    int queue_count;
    redis_client.RPUSH("queues", ss.str(), queue_count);
    return std::make_pair(queue_count - 1, queue_hash);
}

Queue Api::get_queue(unsigned long queue_id) {
    std::vector<std::string> queues_res;
    redis_client.LRANGE("queues", (int)queue_id, (int)queue_id, queues_res);
    if (queues_res.empty()) {
        std::stringstream ss;
        ss << "invalid queue id: " << queue_id;
        throw std::runtime_error(ss.str());
    }

    auto first_pos = queues_res[0].find(':');
    auto second_pos = queues_res[0].find(':', first_pos + 1);
    Queue res;

    res.name = base64decode(queues_res[0].substr(0, first_pos));
    res.key = queues_res[0].substr(first_pos + 1, second_pos - first_pos - 1);
    res.owner = queues_res[0].substr(second_pos + 1, queues_res[0].size() - second_pos - 1);
    return res;
}

std::string Api::add_ticket(unsigned long queue_id, std::string &title, std::string &description) {
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


std::vector<Ticket> Api::find_tickets(unsigned long queue_id, const std::string &ticket_id, const std::string &title,
                                      const std::string &description)  {
    auto queue = get_queue(queue_id);
    std::stringstream queue_to_tickets_key;
    queue_to_tickets_key << "queues/" << queue_id;

    if (!ticket_id.empty()) {
        if (!is_ticket_correct(queue, ticket_id)) {
            throw std::runtime_error("invalid ticket id");
        }

        if (!title.empty() && !description.empty()) {
            Hasher::perform_hashing(ticket_id, title, description);
            if (cache.find(digest) != cache.end()) {
                return cache[digest];
            }
        }

        int ticket_sub_id = get_ticket_sub_id(ticket_id);

        std::vector<std::string> res;
        redis_client.LRANGE(queue_to_tickets_key.str(), ticket_sub_id, ticket_sub_id, res);

        std::vector<Ticket> ticket_res;
        for (auto &dumped_ticket: res) {
            ticket_res.push_back(load_ticket(dumped_ticket));
        }

        if (!title.empty() && !description.empty()) {
            cache[digest] = ticket_res;
        }
        return ticket_res;
    }

    std::vector<Ticket> title_filtered_res;

    if (!title.empty()) {
        std::vector<std::string> res;
        redis_client.LRANGE(queue_to_tickets_key.str(), 0, -1, res);

        if (res.empty()) {
            return {};
        }

        for (auto &dumped_ticket: res) {
            auto ticket = load_ticket(dumped_ticket);

            if (ticket.title.find(title) != std::string::npos) {
                title_filtered_res.push_back(ticket);
            }
        }

        if (title_filtered_res.empty()) {
            return {};
        }
    }

    if (!description.empty()) {
        std::vector<Ticket> final_res;
        for (auto& t: title_filtered_res) {
            if (t.description.find(description) != std::string::npos) {
                final_res.push_back(t);
            }
        }
        return final_res;
    }

    return title_filtered_res;
}
