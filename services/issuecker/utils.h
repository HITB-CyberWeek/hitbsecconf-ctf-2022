#ifndef ISSUECKER_UTILS_H
#define ISSUECKER_UTILS_H
#include <string>

std::string base64encode(const std::string& source);

std::string base64decode(const std::string& source);

std::string get_queue_hash(std::string_view name);

#endif //ISSUECKER_UTILS_H
