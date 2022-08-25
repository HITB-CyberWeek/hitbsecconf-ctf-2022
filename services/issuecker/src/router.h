#ifndef ISSUECKER_ROUTER_H
#define ISSUECKER_ROUTER_H
#include <vector>
#include <unordered_map>

#include "api.h"
#include "json.h"
#include "validators.h"


using HandlerType = std::function<void(Api&, const nlohmann::basic_json<>&, const std::string&)>;


class Router {
public:
    static void add_route(const std::string& path, const HandlerType& handler, const ValidatorType& validator, bool need_auth);
    static std::tuple<HandlerType, ValidatorType, bool> route(const std::string& path);
private:
    static std::unordered_map<std::string, HandlerType> handlers;
    static std::unordered_map<std::string, ValidatorType> validators;
    static std::unordered_map<std::string, bool> auth_requirements;
};


#endif //ISSUECKER_ROUTER_H
