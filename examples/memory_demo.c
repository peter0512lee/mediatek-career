#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void inspect(const uint8_t *data, size_t length) {
    /* sizeof data is the pointer size, never the caller's array length. */
    printf("pointer_size=%zu length=%zu bytes=", sizeof data, length);
    for (size_t i = 0; i < length; i++) printf("%02x ", (unsigned)data[i]);
    putchar('\n');
}
int main(void) {
    uint8_t original[] = {0x41, 0x00, 0x42, 0xff};
    size_t length = sizeof original;
    uint8_t *copy = malloc(length);
    if (!copy) return 1;
    memcpy(copy, original, length);
    original[0] = 0x43;
    inspect(original, length);
    inspect(copy, length); /* A copy has independent contents. */
    free(copy);
    copy = NULL; /* Does not invalidate other aliases automatically. */
    return 0;
}
