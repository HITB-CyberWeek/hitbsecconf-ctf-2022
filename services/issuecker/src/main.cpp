#include <cgicc/Cgicc.h>
#include "handlers.h"
#include "json.h"
#include "router.h"
#include "utils.h"

using namespace cgicc;


std::string get_user_from_cookies(Api& api, const std::vector<HTTPCookie>& cookies) {
    std::string username, secret;
    for (auto& cookie: cookies) {
        if (cookie.getName() == "username") {
            username = cookie.getValue();
        }
        if (cookie.getName() == "secret") {
            secret = cookie.getValue();
        }
    }

    if (api.sm.validate_session(username, secret)) {
        return username;
    }
    return "";
}

int main(int argc, char **argv, char **envp) {
    RedisConfig redis_config{"redis:6379", ""};
    Api api(redis_config);

    Router::add_route("/register", register_handler, validate_user_pair_req, false);
    Router::add_route("/login", login_handler, validate_user_pair_req, false);
    Router::add_route("/add_queue", add_queue_handler, validate_add_queue_req, true);
    Router::add_route("/add_ticket", add_ticket_handler, validate_add_ticket_req, true);
    Router::add_route("/find_tickets", find_tickets_handler, validate_find_tickets_req, true);

    Cgicc cgi;

    auto path = cgi.getEnvironment().getPathInfo();

    if (path.empty()) {
        index_handler();
        return 0;
    }

    auto [handler, validator, need_auth] = Router::route(path);

    if (handler == nullptr) {
        not_found_handler(path);
        return 0;
    }

    std::string username;

    if (need_auth) {
        username = get_user_from_cookies(api, cgi.getEnvironment().getCookieList());
        if (username.empty()) {
            auth_required_handler();
            return 0;
        }
    }

    try {
        auto json_req = nlohmann::json::parse(cgi.getEnvironment().getPostData());
        if (!validator(json_req)) {
            invalid_json_schema_handler();
            return 0;
        }
        handler(api, json_req, username);
    } catch (const nlohmann::json::parse_error& e) {
        invalid_json_format_handler();
    }
    return 0;
}
