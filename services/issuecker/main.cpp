#include "crow.h"

#include <sstream>
#include <utility>
#include <regex>


std::string get_queue_hash(std::string_view name) {
    auto res = name[0] * pow(10, 0);

    for (int i = 0; i < name.length(); ++i) {
        res += name[i] * pow(10, i);
    }
    std::stringstream s;
    s << res;
    return s.str();
}


struct Queue {
    std::string name;
    std::string key;
};


struct Ticket {
    std::string id;
    std::string title;
    std::string description;
};


struct Query {
    long long queue_id;
    unsigned long ticket_id_len;
    unsigned long title_len;
    unsigned long description_len;
    char composed_query[300];
};


struct Context {
    std::vector<Queue> queues;
    std::vector<std::unordered_map<std::string, Ticket>> queue_id_to_tickets;

    std::pair<long long, std::string> add_queue(std::string& name) {
        std::lock_guard _(mtx);
        auto queue_id = queues.size();
        auto queue_hash = get_queue_hash(name);

        Queue q = {queue_hash, queue_hash};
        queues.push_back(q);
        std::unordered_map<std::string, Ticket> empty_tickets;
        queue_id_to_tickets.push_back(empty_tickets);
        return std::make_pair(queue_id, queue_hash);
    }

    std::string add_ticket(long long queue_id, std::string& title, std::string& description) {
        std::lock_guard _(mtx);
        _check_queue_id(queue_id);

        auto ticket_id = queues[queue_id].key + "-" + std::to_string(queue_id_to_tickets[queue_id].size());
        queue_id_to_tickets[queue_id][ticket_id] = {ticket_id, title, description};

        return ticket_id;
    }

    std::vector<Ticket> find_ticket(Query& query) {
        std::lock_guard _(mtx);
        _check_queue_id(query.queue_id);

        if (query.ticket_id_len) {
            auto ticket_id = std::string(query.composed_query);
            if (queue_id_to_tickets[query.queue_id].find(ticket_id) == queue_id_to_tickets[query.queue_id].end()) {
                return {};
            }
            return {queue_id_to_tickets[query.queue_id][ticket_id]};
        }

        throw std::runtime_error("not implemented");
    }

private:
    void _check_queue_id(long long queue_id) const {
        if (queue_id >= queues.size()) {
            throw std::runtime_error("invalid queue id");
        }
    }

    std::mutex mtx;
};


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


template<class Field, class ...Fields, class FuncType>
constexpr auto require_params(Field&& field, Fields&..., FuncType func) {
    return [func, &field](const crow::request& req) -> crow::response {
        auto x = crow::json::load(req.body);
        if (!x.has(field)) {
            std::stringstream ss;
            ss << "field '" << field << "' is required";
            crow::json::wvalue res_json;
            res_json["error"] = ss.str();
            return {res_json};
        }
        return func(x);
    };
}


int main() {
    Context context;
    crow::App<> app;

    std::string queue_name = "abcdef";
    context.add_queue(queue_name);

    std::string title = "title";
    std::string description = "description";

    CROW_LOG_DEBUG << "new ticket_id:" << context.add_ticket(0, title, description);
    std::cout << "new ticket_id:" << context.add_ticket(0, title, description);

    CROW_ROUTE(app, "/add_queue")
            .methods("POST"_method)
                    (require_params("name", [&context](const crow::json::rvalue& x) {
                        std::string queue_name = x["name"].s();

                        auto [queue_id, queue_hash] = context.add_queue(queue_name);

                        CROW_LOG_INFO << "Queue: " << queue_id << " " << queue_hash;

                        std::stringstream res;
                        res << "{\"queue_id\": " << queue_id << "}";
                        return crow::response{res.str()};
                    }));

    CROW_ROUTE(app, "/add_ticket")
            .methods("POST"_method)
                    ([&context](const crow::request &req) {
                        auto x = crow::json::load(req.body);
                        if (!x)
                            return crow::response(400, "invalid json");
                        auto queue_id = x["queue_id"].i();

                        std::string ticket_title = x["title"].s();
                        std::string ticket_description = x["description"].s();

                        try {
                            auto ticket_id = context.add_ticket(queue_id, ticket_title, ticket_description);
                            CROW_LOG_INFO << "Create ticket: " << queue_id << " " << ticket_title << " " << ticket_description << " " << ticket_id;

                            crow::json::wvalue res_json;
                            res_json["ticket_id"] = ticket_id;
                            return crow::response(res_json);

                        } catch (std::runtime_error& e) {
                            return crow::response(400, e.what());
                        }

                    });

    CROW_ROUTE(app, "/find_ticket")
            ([&context](const crow::request &req) {
                auto x = crow::json::load(req.body);

                if (!x)
                    return crow::response(400, "invalid json");

                auto queue_id = x["queue_id"].i();

                Query query{};
                query.queue_id = queue_id;
                query.ticket_id_len = 0;
                query.description_len = 0;
                query.title_len = 0;

                if (x.has("ticket_id")) {
                    std::string ticket_id = x["ticket_id"].s();
                    CROW_LOG_DEBUG << "ticket id: " << ticket_id;

                    if (!is_ticket_correct(context.queues[queue_id], ticket_id)) {
                        return crow::response(400, "invalid ticket_id");
                    }

                    strcpy(query.composed_query, ticket_id.c_str());
                    query.ticket_id_len = ticket_id.length();
                    query.composed_query[query.ticket_id_len] = '\0';
                }
                if (x.has("title")) {
                    std::string ticket_title = x["title"].s();
                    CROW_LOG_DEBUG << "ticket title: " << ticket_title;

                    if (!is_title_correct(ticket_title)) {
                        return crow::response(400, "invalid title");
                    }

                    strcpy(&query.composed_query[query.ticket_id_len + 1], ticket_title.c_str());
                    query.title_len = ticket_title.length();
                    query.composed_query[query.ticket_id_len + 1 + query.title_len] = '\0';
                }
                if (true) {

                    std::string ticket_description = crow::utility::base64decode(x["description"].s());
//                    std::string ticket_description = x["description"].s();
                    CROW_LOG_DEBUG << "ticket description: " << ticket_description;

                    if (!is_description_correct(ticket_description)) {
                        return crow::response(400, "invalid description");
                    }

                    strcpy(&query.composed_query[query.ticket_id_len + 1 + query.title_len + 1], ticket_description.c_str());
                    query.description_len = ticket_description.length();
                    query.composed_query[query.ticket_id_len + 1 + query.title_len + 1 + query.description_len] = '\0';
                }

                crow::json::wvalue res_json;
                try {
                    auto res = context.find_ticket(query);

                    res_json["ticket_count"] = res.size();

                } catch (std::runtime_error& e) {
                    res_json["error"] = e.what();
                }
                return crow::response(res_json);
            });

    app.loglevel(crow::LogLevel::DEBUG);

    app.port(8080)
            .multithreaded()
            .run();
}
