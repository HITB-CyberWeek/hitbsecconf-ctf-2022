#ifndef CRS_VALIDATE_H
#define CRS_VALIDATE_H

#include <stdbool.h>

int validate_charset(const char *s, int buf_size, bool extended);
int validate_string(int client, const char *s, int buf_size, int min_len, int max_len, bool extended);

#endif //CRS_VALIDATE_H
