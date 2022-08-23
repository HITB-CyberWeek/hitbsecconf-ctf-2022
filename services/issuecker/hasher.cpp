#include <cstring>
#include "hasher.h"


Hasher::Hasher()  {
    digest.resize(HASH_SIZE, 0);
}

void Hasher::perform_hashing(const std::string &ticket_id, const std::string &title, const std::string &description)  {
    char blob[MAX_BLOB_LEN];

    std::memcpy(blob, ticket_id.c_str(), ticket_id.length());
    std::memcpy(blob + ticket_id.length(), title.c_str(), title.length());
    std::memcpy(blob + ticket_id.length() + title.length(), description.c_str(), description.length());

    for (int i = 0; i < MAX_BLOB_LEN; ++i) {
        digest[i % HASH_SIZE] = (char) ((digest[i % HASH_SIZE] + blob[i] * blob[(i * 2) % MAX_BLOB_LEN] ^ i) % 256);
    }
}
