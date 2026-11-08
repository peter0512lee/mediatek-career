/* Teaching format only; not compatible with any vendor modem trace. */
#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

_Static_assert(CHAR_BIT == 8, "This teaching wire format requires 8-bit bytes");
enum { HEADER = 16, MAX_PAYLOAD = 32, MAX_FRAME = HEADER + MAX_PAYLOAD };
enum result { INVALID = -1, NEED_MORE = 0, OK = 1 };
struct record {
    uint8_t level;
    uint16_t event_id, length;
    uint32_t sequence, timestamp;
    const uint8_t *payload; /* Borrowed from input; caller retains ownership. */
};
static uint16_t le16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}
static uint32_t le32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static void put16(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8);
}
static void put32(uint8_t *p, uint32_t v) {
    for (unsigned i = 0; i < 4; i++) p[i] = (uint8_t)(v >> (8 * i));
}
/* data points to at least n valid bytes; out and used must be valid. */
static enum result parse_record(const uint8_t *data, size_t n,
                                struct record *out, size_t *used) {
    *used = 0;
    if (n < HEADER) return NEED_MORE;
    if (data[0] != 'L' || data[1] != 'G' || data[2] != 1 || data[3] > 3)
        return INVALID;
    uint16_t length = le16(data + 4);
    if (length > MAX_PAYLOAD) return INVALID;
    if ((size_t)length > n - HEADER) return NEED_MORE;
    uint16_t event = le16(data + 6);
    if ((event == 1 && length != 2) ||
        (event == 2 && (length != 1 || data[HEADER] > 1))) return INVALID;
    *out = (struct record){data[3], event, length,
                          le32(data + 8), le32(data + 12), data + HEADER};
    *used = HEADER + length;
    return OK;
}
static size_t encode(uint8_t out[MAX_FRAME], uint16_t event, uint32_t sequence,
                     uint32_t timestamp, const uint8_t *payload, size_t length) {
    if (length > MAX_PAYLOAD) return 0;
    out[0] = 'L'; out[1] = 'G'; out[2] = 1; out[3] = 2;
    put16(out + 4, (uint16_t)length); put16(out + 6, event);
    put32(out + 8, sequence); put32(out + 12, timestamp);
    if (length) memcpy(out + HEADER, payload, length);
    return HEADER + length;
}
static void print_record(const struct record *r) {
    printf("seq=%lu time_ms=%lu level=%u event=%u len=%u ",
           (unsigned long)r->sequence, (unsigned long)r->timestamp,
           (unsigned)r->level, (unsigned)r->event_id, (unsigned)r->length);
    if (r->event_id == 1) printf("MEASUREMENT value=%u", (unsigned)le16(r->payload));
    else if (r->event_id == 2) printf("STATE value=%u", (unsigned)r->payload[0]);
    else {
        printf("UNKNOWN payload=");
        for (size_t i = 0; i < r->length; i++) printf("%02x", (unsigned)r->payload[i]);
    }
    putchar('\n');
}
static int generate(const char *path) {
    FILE *f = fopen(path, "wb");
    if (!f) { perror(path); return 1; }
    uint8_t frame[MAX_FRAME], measurement[] = {0x34, 0x12}, state[] = {1};
    size_t n = encode(frame, 1, 1, 1000, measurement, sizeof measurement);
    int failed = fwrite(frame, 1, n, f) != n;
    n = encode(frame, 2, 2, 1010, state, sizeof state);
    if (!failed) failed = fwrite(frame, 1, n, f) != n;
    if (fclose(f) != 0) failed = 1;
    if (failed) fprintf(stderr, "write failed\n");
    return failed;
}
static int decode(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); return 1; }
    uint8_t chunk[7], frame[MAX_FRAME];
    size_t held = 0, got, count = 0;
    int failed = 0;
    /* Deliberately split reads: transport chunks are not record boundaries. */
    while (!failed && (got = fread(chunk, 1, sizeof chunk, f)) > 0) {
        for (size_t i = 0; i < got; i++) {
            if (held == sizeof frame) { failed = 1; break; }
            frame[held++] = chunk[i];
            struct record r;
            size_t used;
            enum result status = parse_record(frame, held, &r, &used);
            if (status == INVALID) {
                fprintf(stderr, "invalid frame after %zu records\n", count);
                failed = 1; break;
            }
            if (status == OK) {
                /* Decode before recycling the borrowed payload storage. */
                print_record(&r); count++;
                assert(used == held); held = 0;
            }
        }
    }
    if (ferror(f)) { fprintf(stderr, "read failed\n"); failed = 1; }
    if (!failed && held) { fprintf(stderr, "truncated frame: %zu pending bytes\n", held); failed = 1; }
    if (fclose(f) != 0) failed = 1;
    if (fflush(stdout) == EOF) failed = 1;
    return failed;
}
/* Single-thread model. The count representation uses all four slots. */
struct ring { unsigned data[4]; size_t head, tail, count; unsigned dropped; };
static int push(struct ring *r, unsigned value) {
    if (r->count == 4) { r->dropped++; return 0; }
    r->data[r->head] = value; r->head = (r->head + 1) % 4; r->count++; return 1;
}
static int pop(struct ring *r, unsigned *value) {
    if (!r->count) return 0;
    *value = r->data[r->tail]; r->tail = (r->tail + 1) % 4; r->count--; return 1;
}
static void ring_demo(void) {
    struct ring r = {0};
    for (unsigned i = 1; i <= 6; i++) (void)push(&r, i);
    printf("produced=6 queued=%zu dropped=%u\n", r.count, r.dropped);
    unsigned value;
    while (pop(&r, &value)) printf("consumed=%u\n", value);
}
static void self_test(void) {
    uint8_t frame[MAX_FRAME], payload[] = {0x34, 0x12};
    size_t n = encode(frame, 1, UINT32_MAX, 1000, payload, sizeof payload), used;
    struct record r;
    for (size_t i = 0; i < n; i++) assert(parse_record(frame, i, &r, &used) == NEED_MORE);
    assert(parse_record(frame, n, &r, &used) == OK && used == n);
    assert(r.sequence == UINT32_MAX && r.timestamp == 1000 && le16(r.payload) == 0x1234);
    frame[2] = 2; assert(parse_record(frame, n, &r, &used) == INVALID); frame[2] = 1;
    put16(frame + 4, 33); assert(parse_record(frame, n, &r, &used) == INVALID);
    n = encode(frame, 99, 0, 0, payload, 0);
    assert(parse_record(frame, n, &r, &used) == OK && r.length == 0);
    struct ring q = {0}; unsigned v;
    assert(!pop(&q, &v));
    for (unsigned cycle = 0; cycle < 10; cycle++) {
        for (unsigned i = 0; i < 4; i++) assert(push(&q, cycle * 4 + i));
        assert(!push(&q, 999));
        for (unsigned i = 0; i < 4; i++) { assert(pop(&q, &v)); assert(v == cycle * 4 + i); }
    }
    assert(q.count == 0 && q.dropped == 10);
    puts("self-test: PASS");
}
int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "self-test") == 0) { self_test(); return 0; }
    if (argc == 2 && strcmp(argv[1], "ring") == 0) { ring_demo(); return 0; }
    if (argc == 3 && strcmp(argv[1], "generate") == 0) return generate(argv[2]);
    if (argc == 3 && strcmp(argv[1], "decode") == 0) return decode(argv[2]);
    fprintf(stderr, "usage: %s self-test | ring | generate FILE | decode FILE\n", argv[0]);
    return 2;
}
