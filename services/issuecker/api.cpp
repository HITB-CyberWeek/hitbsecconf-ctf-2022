#include <regex>
#include "api.h"


std::string get_queue_hash(std::string_view name) {
    auto res = name[0] * pow(10, 0);

    for (int i = 0; i < name.length(); ++i) {
        res += name[i] * pow(10, i);
    }
    std::stringstream s;
    s << res;
    return s.str();
}


std::string base64encode(const std::string& source) {
    auto size = boost::beast::detail::base64::encoded_size(source.size());
    char* res = new char[size];
    boost::beast::detail::base64::encode(res, source.data(), size);
    return {res};
}


std::string base64decode(const std::string& source) {
    auto size = boost::beast::detail::base64::decoded_size(source.size());
    char* res = new char[size];
    boost::beast::detail::base64::decode(res, source.data(), size);
    return {res};
}

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


bool api::validate_password(const std::string &username, const std::string &password) {
    std::string expected_hash;
    redis_client.HGET("p_hashes", username, expected_hash);
    std::string real_hash = boost::compute::detail::sha1(password);
    return expected_hash == real_hash;
}

void api::register_user(const std::string &username, const std::string &password) {
    std::string p_hash = boost::compute::detail::sha1(password);
    int res;
    redis_client.HSET("p_hashes", username, p_hash, res);
}

bool api::is_user_exists(const std::string &username) {
    int exists;
    redis_client.HEXISTS("p_hashes", username, exists);
    return (bool)exists;
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
