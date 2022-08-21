#include <regex>
#include <iostream>
#include "api.h"
#include "utils.h"


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


void DumpedQuery::set_queue_id(const std::string &queue_id) {
    add_field(queue_id, queue_id_len);
}

void DumpedQuery::set_ticket_id(const std::string &ticket_id) {
    add_field(ticket_id, ticket_id_len);
}

void DumpedQuery::set_title(const std::string &title) {
    add_field(title, title_len);
}

void DumpedQuery::set_description(const std::string &description) {
    add_field(description, description_len);
}

std::string DumpedQuery::dump() {
    auto res_size = boost::beast::detail::base64::encoded_size(DUMP_SIZE);
    auto res = new char[res_size];
    boost::beast::detail::base64::encode(res, composed_query, res_size);

    return {res};
}

void DumpedQuery::add_field(const std::string &fld_value, unsigned long &fld_len) {
    fld_len = fld_value.length();
    std::memcpy(composed_query + offset, fld_value.c_str(), fld_len);
    offset += fld_len;
}


bool is_ticket_correct(Queue& queue, std::string& ticket_id) {
    std::stringstream pattern;
    pattern << "^" << queue.key << R"(\-\d{1,6}$)";

    std::regex regexp(pattern.str());
    std::cmatch m;

    return std::regex_match(ticket_id.c_str(), m, regexp);
}


bool is_title_correct(std::string& title) {
    return title.length() <= 100;
}


bool is_description_correct(std::string& title) {
    return title.length() <= 10000;
}
