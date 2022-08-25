#include <cgicc/HTTPStatusHeader.h>
#include <cgicc/HTTPHTMLHeader.h>
#include <cgicc/HTTPCookie.h>
#include "handlers.h"
#include "utils.h"
#include "validators.h"


void bad_request(const char* message, int code = 400) {
    std::cout << cgicc::HTTPStatusHeader(code, message);
}


void create_session_and_set_cookies(Api& api, const std::string& username) {
    auto secret = api.sm.create_session(username);
    auto cookie_header = cgicc::HTTPHTMLHeader();

    cookie_header.setCookie(cgicc::HTTPCookie("secret", secret));
    cookie_header.setCookie(cgicc::HTTPCookie("username", username));

    std::cout << cookie_header;
}


void index_handler() {
    std::cout << "Content-Type: text/plain" << std::endl << std::endl;
    std::cout << "Check out this handlers:" << std::endl;
    std::cout << "  /register" << std::endl;
    std::cout << "  /login" << std::endl;
    std::cout << "  /add_queue" << std::endl;
    std::cout << "  /add_ticket" << std::endl;
    std::cout << "  /find_tickets" << std::endl;
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
        bad_request("invalid user or password");
        return;
    }

    create_session_and_set_cookies(api, username);
}


void add_queue_handler(Api& api, const nlohmann::basic_json<>& req, const std::string& username) {
    auto queue_name = req["queue_name"].get<std::string>();

    auto [queue_id, queue_key] = api.add_queue(queue_name, username);

    nlohmann::json res = {
            {"queue_id",  queue_id},
            {"queue_key", queue_key},
    };

    std::cout << "Content-Type: application/json" << std::endl << std::endl;
    std::cout << res.dump();
}


void add_ticket_handler(Api& api, const nlohmann::basic_json<>& req, const std::string& username) {
    auto queue_id = req["queue_id"].get<unsigned long>();

    auto title = base64decode(req["title"].get<std::string>());
    auto description = base64decode(req["description"].get<std::string>());

    try {
        auto queue = api.get_queue(queue_id);
        if (username != queue.owner) {
            bad_request("invalid queue owner", 403);
            return;
        }

        auto ticket_id = api.add_ticket(queue_id, title, description);
        std::cout << "Content-Type: application/json" << std::endl << std::endl;
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
        title = base64decode(req["title"].get<std::string>());
    }
    if (req.contains("description")) {
        description = base64decode(req["description"].get<std::string>());
    }

    try {
        auto tickets = api.find_tickets(queue_id, ticket_id, title, description);

        nlohmann::json res = nlohmann::json::array();
        for (auto &t: tickets) {
            nlohmann::json ticket_json = {
                    {"description", base64encode(t.description)},
                    {"title",       base64encode(t.title)},
            };
            res.push_back(ticket_json);
        }
        std::cout << "Content-Type: application/json" << std::endl << std::endl;
        std::cout << res.dump();

    } catch (const std::runtime_error &e) {
        bad_request("invalid find params");
    }
}


void not_found_handler(const std::string& path) {
    std::cout << "Content-Type: text/plain" << std::endl << std::endl;
    std::stringstream message;
    message << "path '" << path << "' not found in routing";
    std::cout << cgicc::HTTPStatusHeader(404, message.str());
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
