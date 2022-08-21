#include <regex>
#include <iostream>
#include <unordered_set>
#include "validators.h"


std::regex username_regexp("^[a-zA-Z0-9]{3,20}$");
std::regex queue_name_regexp(R"(^[a-zA-Z0-9\s\.\-]{3,50}$)");
std::regex ticket_title_regexp(R"(^[a-zA-Z0-9\s\.\-]{3,100}$)");
std::regex ticket_description_regexp(R"(^[a-zA-Z0-9\s\.\-]{3,1000}$)");


auto get_validator_with_regexp(std::regex& regexp) {
    return [&regexp](const nlohmann::basic_json<>& obj) -> bool {
        return validate_json_string(obj, regexp);
    };
}


bool validate_queue_name(const nlohmann::basic_json<>& obj) {
    return validate_json_string(obj, queue_name_regexp);
}

bool validate_json_string(const nlohmann::basic_json<>& obj, std::regex& regexp) {
    if (!obj.is_string()) {
        return false;
    }
    std::string str_obj = to_string(obj);
    std::string cropped_str_obj = str_obj.substr(1, str_obj.length() - 2);
    std::cmatch m;

    return std::regex_match(cropped_str_obj.c_str(), m, regexp);
}

bool validate_json_number(const nlohmann::basic_json<>& obj) {
    return obj.is_number_integer() && obj.is_number_unsigned();
}

bool validate_json_object(
        const nlohmann::basic_json<>& obj,
        const std::unordered_map<std::string, ValidatorType>& field_validators,
        const std::unordered_set<std::string>& optional_fields
        ) {
    for (auto& p: field_validators) {
        if (optional_fields.find(p.first) != optional_fields.end()) {
            continue;
        }
        if (!obj.contains(p.first)) {
            return false;
        }
        if (!p.second(obj[p.first])) {
            return false;
        }
    }
    return true;
}

bool validate_user_pair_req(const nlohmann::basic_json<>& obj) {
    return validate_json_object(obj, {
            {"username", get_validator_with_regexp(username_regexp)},
            {"password", get_validator_with_regexp(username_regexp)},
    });
}

bool validate_add_queue_req(const nlohmann::basic_json<>& obj) {
    return validate_json_object(obj, {
            {"queue_name", validate_queue_name},
    });
}

bool validate_add_ticket_req(const nlohmann::basic_json<>& obj) {
    return validate_json_object(obj, {
            {"queue_id", validate_json_number},
            {"title", get_validator_with_regexp(ticket_title_regexp)},
            {"description", get_validator_with_regexp(ticket_description_regexp)},
    });
}

bool validate_find_tickets_req(const nlohmann::basic_json<>& obj) {
    return validate_json_object(obj,
            {
                {"queue_id", validate_json_number},
                {"ticket_id", get_validator_with_regexp(ticket_title_regexp)},
                {"title", get_validator_with_regexp(ticket_title_regexp)},
                {"description", get_validator_with_regexp(ticket_description_regexp)},
            },
            {
                "ticket_id", "title", "description"
            }
        );
}
