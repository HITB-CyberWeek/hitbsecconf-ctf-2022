#ifndef ISSUECKER_VALIDATORS_H
#define ISSUECKER_VALIDATORS_H
#include <regex>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include "json.h"
#include "modesl.h"


using ValidatorType = std::function<bool(const nlohmann::basic_json<>& obj)>;

bool validate_json_string(const nlohmann::basic_json<>& obj, std::regex& regexp);

bool validate_json_object(
        const nlohmann::basic_json<>& obj,
        const std::unordered_map<std::string, ValidatorType>& field_validators,
        const std::unordered_set<std::string>& optional_fields = {}
);

bool validate_user_pair_req(const nlohmann::basic_json<>& obj);

bool validate_add_queue_req(const nlohmann::basic_json<>& obj);

bool validate_add_ticket_req(const nlohmann::basic_json<>& obj);

bool validate_find_tickets_req(const nlohmann::basic_json<>& obj);

bool is_ticket_correct(Queue& queue, const std::string& ticket_id);

bool dummy_validator(const nlohmann::basic_json<>& obj);

#endif //ISSUECKER_VALIDATORS_H
