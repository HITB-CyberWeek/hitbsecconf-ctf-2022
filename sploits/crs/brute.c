#include <string.h>
#include <stdio.h>
#include <stdbool.h>

#define PWD_LEN 6
#define CHARSET_LEN 36

char charset[CHARSET_LEN] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
                    'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
                    'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4',
                    '5', '6', '7', '8', '9'};

char pwd[256];

unsigned int hash(char *s) {
    unsigned char state[4] = {0x12, 0x87, 0x39, 0x9A};
    for (int i = 0; i < strlen(s); ++i) {
        state[0] += ((unsigned int)state[0] + (unsigned int)s[i] * 11) % 227;
        state[1] += ((unsigned int)state[1] + (unsigned int)s[i] * 107) % 199;
        state[2] += ((unsigned int)state[2] + (unsigned int)s[i] * 31) % 251;
        state[3] += ((unsigned int)state[3] + (unsigned int)s[i] * 167) % 229;
        state[1] ^= state[3];
        state[0] += state[2];
        state[1] += 12;
        state[3] += 2;
    }
    return (state[0] << 24) + (state[1] << 16) + (state[2] << 8) + state[3];
}

bool matches(char *user, unsigned int hash) {
    unsigned long len = strlen(user);
    return user[len-1] == (hash & 0xFF) &&
           user[len-2] == ((hash & 0xFF00) >> 8) &&
           user[len-3] == ((hash & 0xFF0000) >> 16);
}

void find(char *user, int pos) {
    for (int i = 0; i < CHARSET_LEN; i++) {
        pwd[pos] = charset[i];
        if (pos == PWD_LEN - 1) {
            if (matches(user, hash(pwd))) {
                printf("%s\n", pwd);
            }
        } else {
            find(user, pos+1);
        }
    }
}

int main(int argc, char **argv) {
    if (argc != 2) {
        printf("Please give LOGIN as argument\n");
        return 1;
    }

    memset(pwd, 0, sizeof(pwd));
    find(argv[1], 0);
}
