#include "ledctrl.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
  enum ROTATION rot;

  if (argc < 2) {
    rot = ROT_0;
  } else {
    int arg_rot = atol(argv[1]);
    if ((arg_rot >= 0) && (arg_rot <= 3)) {
      rot = (enum ROTATION)arg_rot;
    } else {
      printf("rotation needs to be in [0, 3]\n");
      return -1;
    }
  }
  printf("Rotation: %d\n", rot);

  // 1) init words to match ids to a given word
  word w1 = {.size = 3, .ids = {13, 14, 15}};

  // 2) based on rotation, assign the mapped pixel id
  ledgrid g = grid_init();
  grid_print(&g);
  // make rotation
  grid_rotate_word(&g, &w1, rot);
}

ledgrid grid_init() {
  ledgrid g = {0};

  // Corner pixels
  g.arr[0][0] = 0;
  g.arr[0][GRID_SIZE - 1] = 1;
  g.arr[GRID_SIZE - 1][GRID_SIZE - 1] = 2;
  g.arr[GRID_SIZE - 1][0] = 3;

  bool invert_dir = false;
  int id = 3;

  for (int j = 1; j < GRID_SIZE - 1; j++) {
    for (int i = 1; i < GRID_SIZE - 1; i++) {
      if (!invert_dir) {
        // from left to right
        g.arr[j][i] = ++id;

      } else {
        // from right to left
        g.arr[j][GRID_SIZE - 1 - i] = ++id;
      }
    }
    invert_dir = !invert_dir;
  }

  return g;
}

void grid_print(const ledgrid *g) {
  for (int j = 0; j < GRID_SIZE; j++) {
    for (int i = 0; i < GRID_SIZE; i++) {
      int num = g->arr[j][i];
      if (num < 10) {
        printf("  %d ", g->arr[j][i]);
      } else if (num < 100) {
        printf(" %d ", g->arr[j][i]);
      } else {
        printf("%d ", g->arr[j][i]);
      }
    }
    printf("\n");
  }
}

bool grid_rotate_word(const ledgrid *g, word *w, enum ROTATION rot) {
  pixel_lookup lookup = {0};
  int pixels_found = grid_word_lookup(g, w, &lookup);
  if (pixels_found != w->size) {
    printf("Err: Did not found all pixels!\n");
    return false;
  }
  printf("Found all pixels.\n--- Starting rotation\n");

  for (int pi = 0; pi < lookup.size; pi++) {
    pixel_ind ind = lookup.inds[pi];
    /* printf("ind: i=%d, j=%d\n", ind.i, ind.j); */

    /* w->ids[0] = 123; */

    uint pid_rot;

    switch (rot) {
    case ROT_0:
      return true;
    case ROT_90:
      // i=SIZE - j | j=i
      pid_rot = g->arr[ind.i][GRID_SIZE - 1 - ind.j];
      printf("New rotated ind: %d \n", pid_rot);
      break;
    case ROT_180:
      // i=SIZE-1 | j=SIZE-j
      pid_rot = g->arr[GRID_SIZE - 1 - ind.j][GRID_SIZE - 1 - ind.i];
      printf("New rotated ind: %d \n", pid_rot);
      break;
    case ROT_270:
      // i=j | j=SIZE-i
      pid_rot = g->arr[GRID_SIZE - 1 - ind.i][ind.j];
      printf("New rotated ind: %d \n", pid_rot);
      break;
    }
  }

  return true;
}

int grid_word_lookup(const ledgrid *g, word *w, pixel_lookup *lu) {

  int word_ind = 0;

  int fj = -1;
  int fi = -1;

  int done = 0;

  while (word_ind < w->size) {
    for (int j = 0; j < GRID_SIZE && !done; j++) {
      for (int i = 0; i < GRID_SIZE; i++) {

        int pixel_id = g->arr[j][i];
        if (pixel_id == w->ids[word_ind]) {
          // Found i,j indices for pixel id
          fj = j;
          fi = i;
          printf("Found pixel id: %d at (i=%d / j=%d)\n", w->ids[word_ind], fi,
                 fj);

          pixel_ind pind = {.i = fi, .j = fj};
          lu->inds[word_ind] = pind;
          lu->size++;
          done = 1;
          break;
        }
      }
    }
    // while loop, increase word ind
    done = 0;
    word_ind++;
  }

  if (fi == -1) {
    return -1;
  }
  return lu->size;
}
