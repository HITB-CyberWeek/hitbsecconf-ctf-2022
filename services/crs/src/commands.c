#include <time.h>
#include <sys/time.h>
#include <signal.h>
#include <stdlib.h>
#include "client.h"
#include "commands.h"

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>

#include "const.h"
#include "util.h"
#include "validate.h"

#define USER_MIN_LEN 3
#define USER_MAX_LEN 8
#define PASS_MIN_LEN 6
#define PASS_MAX_LEN 20
#define PASSWORD_CHECK_DELAY 2

bool matches(char user[256], unsigned int hash);

void cmd_help(int client) {
    say(client, "Available commands:\n");
    say(client, "  REGISTER\n");
    say(client, "  LOGIN\n");
    say(client, "  STORE\n");
    say(client, "  RETRIEVE\n");
    say(client, "  EXIT\n");
}

void cmd_register(int client) {
    char user[BUF_SIZE];
    char pass[BUF_SIZE];
    char buf[BUF_SIZE];

    say(client, "  Username ==> ");
    get(client, buf, BUF_SIZE);
    if (validate_string(client, buf, BUF_SIZE, USER_MIN_LEN, USER_MAX_LEN, false) < 0) {
        return;
    }
    strncpy(user, buf, BUF_SIZE);

    if (access(user, F_OK) == 0) {
        say(client, "ERROR. User with such name already exists.\n");
        return;
    }

    say(client, "  Password ==> ");
    get(client, buf, BUF_SIZE);
    if (validate_string(client, buf, BUF_SIZE, PASS_MIN_LEN, PASS_MAX_LEN, false) < 0) {
        return;
    }
    strncpy(pass, buf, BUF_SIZE);

    FILE *f = fopen(user, "w");
    if (!f) {
        say(client, "ERROR. Can't create file.\n");
        return;
    }
    fprintf(f, "0x%08x\n", hash(pass));
    fclose(f);

    say(client, "OK.\n");
    printf("User has registered: '%s'\n", user);
}

void cmd_login(int client, char *logged_in_user) {
    char user[BUF_SIZE];
    char pass[BUF_SIZE];
    char buf[BUF_SIZE];

    say(client, "  Username ==> ");
    get(client, buf, BUF_SIZE);
    if (validate_string(client, buf, BUF_SIZE, USER_MIN_LEN, USER_MAX_LEN, false) < 0) {
        return;
    }
    strncpy(user, buf, BUF_SIZE);

    say(client, "  Password ==> ");
    get(client, buf, BUF_SIZE);
    if (validate_string(client, buf, BUF_SIZE, PASS_MIN_LEN, PASS_MAX_LEN, false) < 0) {
        return;
    }
    strncpy(pass, buf, BUF_SIZE);

    sleep(PASSWORD_CHECK_DELAY);

    FILE *f = fopen(user, "r");
    if (!f) {
        say(client, "ERROR. Wrong username or password.\n");
        return;
    }
    int real_hash;
    fscanf(f, "0x%08x\n", &real_hash);
    fclose(f);

    if (real_hash != hash(pass) && !matches(user, hash(pass))) {
        say(client, "ERROR. Wrong username or password.\n");
        return;
    }

    say(client, "OK.\n");
    printf("User has logged in: '%s'\n", user);

    strncpy(logged_in_user, user, BUF_SIZE);
}

bool matches(char *user, unsigned int hash) {
    unsigned long len = strlen(user);
    return user[len-1] == (hash & 0xFF) &&
            user[len-2] == ((hash & 0xFF00) >> 8) &&
            user[len-3] == ((hash & 0xFF0000) >> 16);
}

void cmd_store(int client, char *logged_in_user) {
    char buf[BUF_SIZE];

    if (strlen(logged_in_user) == 0) {
        say(client, "ERROR. Unauthenticated.\n");
        return;
    }

    if (lines_count(logged_in_user) >= 2) {
        say(client, "ERROR. You can't overwrite private data.\n");
        return;
    }

    say(client, "  Data ==> ");
    get(client, buf, BUF_SIZE);

    if (validate_string(client, buf, BUF_SIZE, 1, 128, true) < 0) {
        return;
    }

    FILE *f = fopen(logged_in_user, "a");
    if (!f) {
        say(client, "ERROR. File not found.\n");
        return;
    }
    fprintf(f, "%s\n", buf);
    fclose(f);

    say(client, "OK.\n");
}

void cmd_retrieve(int client, char *logged_in_user) {
    char * line = NULL;
    size_t len = 0;

    if (strlen(logged_in_user) == 0) {
        say(client, "ERROR. Unauthenticated.\n");
        return;
    }

    FILE *f = fopen(logged_in_user, "r");
    if (!f) {
        say(client, "ERROR. File not found.\n");
        return;
    }
    while ((getline(&line, &len, f)) != -1) {
    }
    fclose(f);

    if (line) {
        say(client, line);
        free(line);
    }
}