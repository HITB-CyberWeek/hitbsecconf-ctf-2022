#ifndef ISSUECKER_UTILS_H
#define ISSUECKER_UTILS_H
#include <string>
#define LOG_FILE "/var/log/lighttpd/debug.log"

std::string base64encode(const std::string& source);

std::string base64decode(const std::string& source);

std::string get_queue_hash(std::string_view name);

std::string gen_random_string(uint length);

void log(const std::string& message);

#endif //ISSUECKER_UTILS_H
