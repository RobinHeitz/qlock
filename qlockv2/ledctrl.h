#include <stdbool.h>
#include <stdio.h>

#define NUM_PIXELS_TOTAL 148 // 12 * 12 + 4
#define GRID_SIZE 14
#define MAX_WORD_LENGTH 10
#define NUM_WORDS 6

typedef unsigned int uint;

enum ROTATION {
  ROT_0 = 0,
  ROT_90 = 1,
  ROT_180 = 2,
  ROT_270 = 3,
};

enum WORD_DEFS {
  W_INVALID = -1,
  W_IT_IS = 0,
  W_5 = 1,
  W_10 = 2,
  W_20 = 3,
  W_3_OVER_4 = 4,
  W_1_OVER_4 = 5,
};

typedef struct {
  uint led_id;
  bool state;
  int row_ind;
  int col_ind;
  bool change;
} pixel;

typedef struct {
  uint size;
  pixel pixels[MAX_WORD_LENGTH];
} word;

typedef struct {
  int size;
  enum WORD_DEFS keys[NUM_WORDS];
  word values[NUM_WORDS];
} word_map;

typedef struct {
  int arr[GRID_SIZE][GRID_SIZE];
} ledgrid;

typedef struct {
  int month; // 1-12
  int day;   // 1-31
  bool weekend;
  int hour; // 0-23
  int min;  // 0-59
  int sec;  // 0-60;
} qlock_time;

void words_init(word_map *map);

int word_initp(word *w, uint size, const int *ids);
word word_init(uint size, const int *ids);
void word_print(word *w);
void word_setstate(word *w, bool state);

ledgrid grid_init();
void grid_print(const ledgrid *g);
int grid_word_lookup(const ledgrid *g, word *w);
bool grid_rotate_word(const ledgrid *g, word *w, enum ROTATION rot);

word_map word_map_init();
bool word_map_add(word_map *m, enum WORD_DEFS key, const word w);
int word_map_get(word_map *m, enum WORD_DEFS key, word **out);
word *word_map_getp(word_map *m, enum WORD_DEFS key);
