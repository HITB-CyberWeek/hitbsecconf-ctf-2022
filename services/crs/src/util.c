#include "util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#include "const.h"

void say(int sock, char* message) {
    send(sock, message,strlen(message), 0);
}

void get(int sock, char *b, int buf_size) {
    memset(b, 0, BUF_SIZE);
    int started = 0;
    for (int i = 0; i < buf_size-1;) {
        ssize_t count = recv(sock, b+i, 1, 0);
        if (count < 0) {
            perror("error: recv");
            exit(0);
        }
        if (count == 0) {
            // no message was received from the peer, and we are confident that none will be forthcoming
            printf("Peer has disconnected\n");
            exit(0);
        }
        if (b[i] == '\n' || b[i] == '\r') {
            if (!started) {
                continue; // Skip newlines at start.
            }
            b[i] = '\0';
            break;
        } else {
            started = 1;
            i++;
        }
    }
    printf("Request from client: '%s'.\n", b);
}

// hash("h4ck3r") = 0xd7c94a59
// hash("p918aj") = 0x2a90c1df
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

int lines_count(char *filename) {
    char * line = NULL;
    size_t len = 0;

    FILE *f = fopen(filename, "r");
    if (!f) {
        return -1;
    }
    int lines = 0;
    while ((getline(&line, &len, f)) != -1) {
        lines += 1;
    }
    fclose(f);
    if (line) {
        free(line);
    }
    return lines;
}