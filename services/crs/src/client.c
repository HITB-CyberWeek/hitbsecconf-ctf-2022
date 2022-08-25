#include "client.h"

#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <stdbool.h>

#include "const.h"
#include "commands.h"
#include "util.h"

#define CLIENT_TIMEOUT 60  // Seconds
#define CMD_DELAY 5 // Seconds

char buf[BUF_SIZE] = {0};
char logged_in_user[BUF_SIZE] = {0};
time_t last_cmd_time = 0;

void handle_alarm(int sig) {
    printf("Client has timed out, terminating child process\n");
    exit(1);
}

void handle_client(int client, char *client_str) {
    struct itimerval it_val;
    bool client_logged = false;

    signal(SIGALRM, handle_alarm);
    it_val.it_value.tv_sec = CLIENT_TIMEOUT;
    it_val.it_value.tv_usec = 0;
    it_val.it_interval = it_val.it_value;
    setitimer(ITIMER_REAL, &it_val, NULL);

    say(client, "=======================================================\n");
    say(client, "Enterprise Systems CRS / GDS Welcome. Build 6.1672.1928\n");
    say(client, "=======================================================\n\n");
    say(client, "Attention: all activity is logged.\n\n");

    while (1) {
        if (strlen(logged_in_user) > 0) {
            say(client, "[");
            say(client, logged_in_user);
            say(client, "] ");
        }
        say(client, "Command ==> ");
        get(client, buf, BUF_SIZE);
        if (!client_logged) {
            printf("Client address is %s.\n", client_str);
            client_logged = true;
        }

        // Commands rate limiting per connection.
        if (last_cmd_time != 0) {
            time_t delta_seconds = time(0) - last_cmd_time;
            if (delta_seconds < CMD_DELAY) {
                say(client, "ERROR. Too fast command retransmission.\n\n");
                last_cmd_time = time(0);
                continue;
            }
        }
        last_cmd_time = time(0);

        // Commands parsing.
        if (0 == strcasecmp(buf, "help")) {
            cmd_help(client);
        } else if (0 == strcasecmp(buf, "register")) {
            cmd_register(client);
        } else if (0 == strcasecmp(buf, "login")) {
            cmd_login(client, logged_in_user);
        } else if (0 == strcasecmp(buf, "store")) {
            cmd_store(client, logged_in_user);
        } else if (0 == strcasecmp(buf, "retrieve")) {
            cmd_retrieve(client, logged_in_user);
        } else if (0 == strcasecmp(buf, "exit")) {
            break;
        } else {
            say(client, "ERROR. Unknown command.\n");
        }
        say(client, "\n");
    }
    say(client, "BYE.\n");
}

