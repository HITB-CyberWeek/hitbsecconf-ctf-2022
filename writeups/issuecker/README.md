# Issuecker

## Description
Issuecker is a simple issue tracker.
Allowed method: `register`, `login`, `add_queue`, `add_ticket`, `find_tickets`
See API more detailed description [there](https://github.com/HITB-CyberWeek/hitbsecconf-ctf-2022/blob/main/writeups/issuecker/API.md).

## Ticket id
Every ticket id has following format: `<queue_key>-<ticket_sub_id>`
where ticket_sub_id is a non-negative number of ticket in queue. For queue key generation issuecker uses following function:


```
std::string get_queue_hash(std::string_view name) {
    auto res = name[0] * pow(2, 0);

    for (int i = 0; i < name.length(); ++i) {
        res += ((uint)(name[i] * pow(2, (i % 10))) % (uint)(i % 100 + 1)) * 1749;
    }
    std::stringstream ss;
    ss << res;
    return ss.str();
}
```

Function `pow` has a `double` return type, so variable `res` as the same type. For writing `double` value to the `std::stringstream` C++ uses exponential notation for all number greater than 1000000. It means that any queue hash greater than 1000000 will be converted to `std::string` with following format: `1.01917e+06`.

Field `ticket_id` is validated by pattern: `^<queue_key>-<ticket_sub_id>$` in every `/find_tickets` request. It leads to incorrect regex for every queue with 
key greater than 1000000. For example with queue name `R2k4OdSVXJ5Q7jc5QPgXqU3z8R7lzhZNmYASATeH`
and ticket with sub_id `123`, ticket has the following validation pattern: `^1.01917e+06-123$`.
So we can bypass validation with values with repeated `e` symbol, for example ticket id:
`1.01917eeeeeeeeeeeeeeeeeeeeeeeee06-123` matches the validation pattern.

We can run simple brute-force for finding queue name with queue key greater than 1000000: [gen_queue_name.cpp](https://github.com/HITB-CyberWeek/hitbsecconf-ctf-2022/blob/main/sploits/issuecker/src/gen_queue_name.cpp).

## Buffer overflow
Service has a vulnerable ticket [hash generation](https://github.com/HITB-CyberWeek/hitbsecconf-ctf-2022/blob/main/services/issuecker/src/hasher.cpp#L10): 
```
void Hasher::perform_hashing(const std::string &ticket_id, const std::string &title, const std::string &description)  {
    char blob[MAX_BLOB_LEN];

    std::memcpy(blob, ticket_id.c_str(), ticket_id.length());
    std::memcpy(blob + ticket_id.length(), title.c_str(), title.length());
    std::memcpy(blob + ticket_id.length() + title.length(), description.c_str(), description.length());

    for (int i = 0; i < MAX_BLOB_LEN; ++i) {
        digest[i % HASH_SIZE] = (char) ((digest[i % HASH_SIZE] + blob[i] * blob[(i * 2) % MAX_BLOB_LEN] ^ i) % 256);
    }
}

```

Every `std::memcpy` performs without a size checking, so it leads to buffer overflow
and all data from `ticket_id`, `title` and `description` will be written to the stack.

## Vulnerability
Taking an incorrect queue key generation and invalid hash function together we can bypass ticket id validation (as a consequence, ticket id length limit too) and write to stack anything we pass to description. It allows us to generate a rop-chain and place it on the stack.
