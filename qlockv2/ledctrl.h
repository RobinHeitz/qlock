#include <stdbool.h>
#include <stdio.h>

#define NUM_PIXELS_TOTAL 148 // 12 * 12 + 4
#define GRID_SIZE 14
#define MAX_WORD_LENGTH 10

enum ROTATION {
  ROT_0 = 0,
  ROT_90 = 1,
  ROT_180 = 2,
  ROT_270 = 3,
};

typedef unsigned int uint;

typedef struct {
  uint id;
  bool state;
} pixel;

typedef struct {
  uint size;
  uint ids[GRID_SIZE];
} word;

typedef struct {
  int arr[GRID_SIZE][GRID_SIZE];
} ledgrid;

typedef struct {
  int i;
  int j;
} pixel_ind;

typedef struct {
  pixel_ind inds[MAX_WORD_LENGTH];
  uint size;
} pixel_lookup;

ledgrid grid_init();
void grid_print(const ledgrid *g);
int grid_word_lookup(const ledgrid *g, word *w, pixel_lookup *lu);
bool grid_rotate_word(const ledgrid *g, word *w, enum ROTATION rot);
