#ifndef CRS_VALIDATE_H
#define CRS_VALIDATE_H

int validate_charset(const char *s, int buf_size);
int validate_string(int client, const char *s, int buf_size, int min_len, int max_len);

#endif //CRS_VALIDATE_H
