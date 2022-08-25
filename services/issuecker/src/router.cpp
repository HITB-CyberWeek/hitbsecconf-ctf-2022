#include <iostream>
#include "router.h"
#include "validators.h"

std::unordered_map<std::string, HandlerType> Router::handlers;
std::unordered_map<std::string, ValidatorType> Router::validators;
std::unordered_map<std::string, bool> Router::auth_requirements;

void Router::add_route(const std::string& path, const HandlerType& handler, const ValidatorType& validator, bool need_auth) {
    Router::handlers[path] = handler;
    Router::validators[path] = validator;
    Router::auth_requirements[path] = need_auth;
}


std::tuple<HandlerType, ValidatorType, bool> Router::route(const std::string &path) {
    if (Router::handlers.find(path) == Router::handlers.end()) {
        return {nullptr, nullptr, false};
    }
    return {Router::handlers[path], Router::validators[path], Router::auth_requirements[path]};
}
