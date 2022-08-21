#include <cgicc/HTTPStatusHeader.h>
#include <cgicc/HTTPHTMLHeader.h>
#include <cgicc/HTTPCookie.h>
#include "handlers.h"
#include "validators.h"


void bad_request(const char* message, int code = 400) {
//    std::cout << cgicc::HTTPStatusHeader(code, message);
    std::cout << message;
}


void create_session_and_set_cookies(Api& api, const std::string& username) {
    auto secret = api.sm.create_session(username);
    auto cookie_header = cgicc::HTTPHTMLHeader();

    cookie_header.setCookie(cgicc::HTTPCookie("secret", secret));
    cookie_header.setCookie(cgicc::HTTPCookie("username", username));

    std::cout << cookie_header;
}


void register_handler(Api& api, const nlohmann::basic_json<>& req, const std::string&) {
    auto username = req["username"].get<std::string>();
    auto password = req["password"].get<std::string>();

    if (api.is_user_exists(username)) {
        bad_request("user is already exists");
        return;
    }

    api.register_user(username, password);

    create_session_and_set_cookies(api, username);
}


void login_handler(Api& api, const nlohmann::basic_json<>& req, const std::string&) {
    auto username = req["username"].get<std::string>();
    auto password = req["password"].get<std::string>();

    if (!api.validate_password(username, password)) {
        bad_request("invalid user or passowrd");
        return;
    }

    create_session_and_set_cookies(api, username);
}


void add_queue_handler(Api& api, const nlohmann::basic_json<>& req, const std::string& username) {
    auto queue_name = req["queue_name"].get<std::string>();

    auto [queue_id, queue_key] = api.add_queue(queue_name, username);

    std::cout << "queue_id: " << queue_id << " " << queue_key;
}


void add_ticket_handler(Api& api, const nlohmann::basic_json<>& req, const std::string& username) {
    auto queue_id = req["queue_id"].get<unsigned long>();
    auto title = req["title"].get<std::string>();
    auto description = req["description"].get<std::string>();

    try {
        auto queue = api.get_queue(queue_id);
        if (username != queue.owner) {
            bad_request("invalid queue owner", 403);
            return;
        }

        auto ticket_id = api.add_ticket(queue_id, title, description);
        std::cout << R"({"ticket_id": ")" << ticket_id << "\"}";

    } catch (const std::runtime_error& e) {
        bad_request("invalid queue id");
    }
}


void find_tickets_handler(Api& api, const nlohmann::basic_json<>& req, const std::string& username) {
    auto queue_id = req["queue_id"].get<unsigned long>();

    std::string ticket_id;
    std::string title;
    std::string description;

    if (req.contains("ticket_id")) {
        ticket_id = req["ticket_id"].get<std::string>();
    }
    if (req.contains("title")) {
        title = req["title"].get<std::string>();
    }
    if (req.contains("description")) {
        description = req["description"].get<std::string>();
    }

    auto tickets = api.find_tickets(queue_id, ticket_id, title, description);

    nlohmann::json res = nlohmann::json::array();
    for (auto &t: tickets) {
        nlohmann::json ticket_json = {
                {"description", t.description},
                {"title",       t.title},
        };
        res.push_back(ticket_json);
    }
    std::cout << res.dump();
}


void not_found_handler(const std::string& path) {
    std::stringstream message;
    message << "path '" << path << "' not found in routing";
    std::cout << cgicc::HTTPStatusHeader(404, message.str());
    std::cout << message.str();
}


void invalid_json_schema_handler() {
    bad_request("invalid json data");
}

void invalid_json_format_handler() {
    bad_request("invalid json format");
}

void auth_required_handler() {
    bad_request("auth required");
}