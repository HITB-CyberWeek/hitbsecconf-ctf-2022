#include "validate.h"

#include <string.h>

#include "util.h"

int validate_charset(const char *s, int buf_size) {
    for (int i = 0; i < buf_size; i++) {
        if (s[i] == '\0') {
            return 0; // OK
        }
        if ((s[i] >= '0' && s[i] <= '9') || (s[i] >= 'a' && s[i] <= 'z')) {
            continue;
        }
        return -1; // Bad char
    }
    return 0; // OK
}


int validate_string(int client, const char *s, int buf_size, int min_len, int max_len) {
    if (strlen(s) < min_len) {
        say(client, "ERROR. Too short.\n");
        return -1;
    }
    if (strlen(s) > max_len) {
        say(client, "ERROR. Too long.\n");
        return -1;
    }
    if (validate_charset(s, buf_size) < 0) {
        say(client, "ERROR. Wrong character.\n");
        return -1;
    }
    return 0;
}