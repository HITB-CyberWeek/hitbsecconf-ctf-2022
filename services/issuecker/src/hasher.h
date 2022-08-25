#ifndef ISSUECKER_HASHER_H
#define ISSUECKER_HASHER_H
#include <sys/types.h>
#include <string>


const uint MAX_TICKET_LEN = 50;
const uint MAX_TITLE_LEN = 100;
const uint MAX_DESCRIPTION_LEN = 1500;
const uint MAX_BLOB_LEN = MAX_TICKET_LEN + MAX_TITLE_LEN + MAX_DESCRIPTION_LEN;
const uint HASH_SIZE = 100;


static std::string digest;


class Hasher {
public:
    Hasher();

    static void perform_hashing(const std::string& ticket_id, const std::string& title, const std::string& description);
};


#endif //ISSUECKER_HASHER_H
