#include <string.h>
#include <stdio.h>
#include <stdbool.h>

#define PASS_LEN 6
#define CHARSET_LEN 36
#define DELTA ('z' - '0' + 1)

char charset[CHARSET_LEN] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
                    'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
                    'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4',
                    '5', '6', '7', '8', '9'};

char pass[PASS_LEN + 1];
char met[DELTA * DELTA * DELTA];

bool is_alnum(char c) {
    return ('0' <= c && c <= '9') || ('a' <= c && c <= 'z');
}

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

void find(char *pass, int pos) {
    for (int i = 0; i < CHARSET_LEN; i++) {
        pass[pos] = charset[i];
        if (pos == PASS_LEN - 1) {
            int value = hash(pass);
            char x = (char) ((value & 0xFF0000) >> 16);
            char y = (char) ((value & 0xFF00) >> 8);
            char z = (char) (value & 0xFF);
            if (is_alnum(x) && is_alnum(y) && is_alnum(z)) {
                int idx = (x - '0') * DELTA * DELTA +
                        (y - '0') * DELTA +
                        (z - '0');
                if (met[idx] == 0) {
                    printf("%c%c%c : %s\n", x, y, z, pass);
                    met[idx] = 1;
                }
            }
        } else {
            find(pass, pos + 1);
        }
    }
}

int main(int argc, char **argv) {
    memset(pass, 0, sizeof pass);
    memset(met, 0, sizeof met);
    find(pass, 0);
}
