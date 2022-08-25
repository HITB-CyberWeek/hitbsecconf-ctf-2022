#ifndef CRS_UTIL_H
#define CRS_UTIL_H

void say(int sock, char* message);
void get(int sock, char *b, int buf_size);
unsigned int hash(char *s);
int lines_count(char *filename);

#endif //CRS_UTIL_H
