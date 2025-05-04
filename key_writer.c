#include <stdio.h>
#include <string.h>

void write_secret(const char* secret, const char* filename) {
    FILE *f = fopen(filename, "w");
    if (f == NULL) return;
    fwrite(secret, 1, strlen(secret), f);
    fclose(f);
}
