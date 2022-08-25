#ifndef CRS_COMMANDS_H
#define CRS_COMMANDS_H

void cmd_help(int client);
void cmd_register(int client);
void cmd_login(int client, char *logged_in_user);
void cmd_store(int client, char *logged_in_user);
void cmd_retrieve(int client, char *logged_in_user);

#endif //CRS_COMMANDS_H
