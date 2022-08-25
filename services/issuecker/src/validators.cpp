#include <regex>
#include <iostream>
#include <sstream>
#include <unordered_set>
#include "validators.h"


std::regex username_regexp("^[a-zA-Z0-9]{3,20}$");
std::regex queue_name_regexp(R"(^[a-zA-Z0-9\s\.\-]{3,40}$)");


bool dummy_validator(const nlohmann::basic_json<>& obj) {
    return true;
}

auto get_validator_with_regexp(std::regex& regexp) {
    return [&regexp](const nlohmann::basic_json<>& obj) -> bool {
        return validate_json_string(obj, regexp);
    };
}

auto get_length_validator(int min, int max) {
    return [min, max](const nlohmann::basic_json<>& obj) -> bool {
        if (!obj.is_string()) {
            return false;
        }
        auto str_obj = obj.get<std::string>();
        return min <= str_obj.length() && str_obj.length() <= max;
    };
}

bool validate_queue_name(const nlohmann::basic_json<>& obj) {
    return validate_json_string(obj, queue_name_regexp);
}

bool validate_json_string(const nlohmann::basic_json<>& obj, std::regex& regexp) {
    if (!obj.is_string()) {
        return false;
    }
    std::string str_obj = obj.get<std::string>();
    std::cmatch m;

    return std::regex_match(str_obj.c_str(), m, regexp);
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
            {"title", get_length_validator(0, 150)},
            {"description", get_length_validator(0, 2000)},
    });
}

bool validate_find_tickets_req(const nlohmann::basic_json<>& obj) {
    return validate_json_object(obj,
            {
                {"queue_id", validate_json_number},
                {"ticket_id", dummy_validator},
                {"title", get_length_validator(0, 150)},
                {"description", get_length_validator(0, 2000)},
            },
            {
                "ticket_id", "title", "description"
            }
        );
}


bool is_ticket_correct(Queue& queue, const std::string& ticket_id) {
    std::stringstream pattern;
    pattern << "^" << queue.key << R"(\-\d{1,6}$)";

    std::regex regexp(pattern.str());
    std::cmatch m;

    return std::regex_match(ticket_id.c_str(), m, regexp);
}
