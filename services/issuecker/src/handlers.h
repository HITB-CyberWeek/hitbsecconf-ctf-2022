#ifndef ISSUECKER_HANDLERS_H
#define ISSUECKER_HANDLERS_H
#include <iostream>
#include "api.h"
#include "json.h"

void not_found_handler(const std::string& path);

void invalid_json_schema_handler();

void invalid_json_format_handler();

void index_handler();

void register_handler(Api& api, const nlohmann::basic_json<>& req, const std::string&);

void login_handler(Api& api, const nlohmann::basic_json<>& req, const std::string&);

void add_queue_handler(Api& api, const nlohmann::basic_json<>& req, const std::string& username);

void add_ticket_handler(Api& api, const nlohmann::basic_json<>& req, const std::string& username);

void find_tickets_handler(Api& api, const nlohmann::basic_json<>& req, const std::string& username);

void auth_required_handler();

#endif //ISSUECKER_HANDLERS_H
