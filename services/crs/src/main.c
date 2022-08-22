#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <signal.h>

#include "client.h"

#define LISTEN_PORT 4444 // TCP

int main() {
    int ret;
    struct sockaddr_in server_addr;

    // Avoid zombies
    signal(SIGCHLD, SIG_IGN);

    int server = socket(AF_INET, SOCK_STREAM, 0);
    if (server < 0) {
        perror("error: socket");
        exit(1);
    }

    int option = 1;
    ret = setsockopt(server, SOL_SOCKET, SO_REUSEADDR, &option, sizeof(option));
    if (ret < 0) {
        perror("error: setsockopt");
        exit(1);
    }

    // Initializing address structure with NULL
    memset(&server_addr, '\0', sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(LISTEN_PORT);
    server_addr.sin_addr.s_addr = INADDR_ANY;
 
    ret = bind(server, (struct sockaddr*)&server_addr, sizeof(server_addr));
    if (ret < 0) {
        perror("error: bind");
        exit(1);
    }
 
    ret = listen(server, 100);
    if (ret < 0) {
        perror("error: listen");
        exit(1);
    }
    printf("Listening TCP port %d...\n", LISTEN_PORT);

    while (1) {
        struct sockaddr_in client_addr;
        socklen_t addr_size = sizeof(client_addr);
        char client_str[64];

        int client = accept(server, (struct sockaddr*)&client_addr, &addr_size);
        if (client < 0) {
            perror("error: accept");
            exit(1);
        }
 
        snprintf(client_str, sizeof client_str, "%s:%d", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        int pid = fork();
        if (pid < 0) {
            perror("error: fork");
            exit(1);
        }
        if (pid == 0) {
            // Child
            close(server);
            handle_client(client, client_str);
            close(client);
            printf("Child process has completed.\n");
            exit(0);
        } else {
            // Parent
            close(client);
        }
    }
}
