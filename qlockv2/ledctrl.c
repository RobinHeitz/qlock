#include "ledctrl.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

qlock_time get_time() {
  time_t rawtime;
  struct tm *timeinfo;
  time(&rawtime);
  timeinfo = localtime(&rawtime);
  /* printf("Current time and date: %s \n", asctime(timeinfo)); */
  /* printf("year %d\n", timeinfo->tm_year); */
  /* printf("month %d\n", timeinfo->tm_mon); */
  /* printf("mday %d\n", timeinfo->tm_mday); */
  /* printf("hour %d\n", timeinfo->tm_hour); */
  /* printf("min %d\n", timeinfo->tm_min); */
  /* printf("sec %d\n", timeinfo->tm_sec); */
  /* printf("wday %d\n", timeinfo->tm_wday); */
  /* printf("yday %d\n", timeinfo->tm_yday); */

  qlock_time qt;
  qt.month = timeinfo->tm_mon + 1;
  qt.day = timeinfo->tm_mday;
  int w_day = timeinfo->tm_wday;
  qt.weekend = w_day == 6 || w_day == 0;
  qt.hour = timeinfo->tm_hour;
  qt.min = timeinfo->tm_min;
  qt.sec = timeinfo->tm_sec;
  return qt;
}

void qlocktime_print(qlock_time *qt) {
  printf("Month: %d Day: %d is weekend: %d | hour: %d, min: %d, sec: %d\n",
         qt->month, qt->day, qt->weekend, qt->hour, qt->min, qt->sec);
}

void set_minute_pixels(word_map *m, qlock_time qt) {
  printf("set minute pixels");
  bool setstate = qt.sec % 2;

  word *word1 = word_map_getp(m, W_10);

  word_print(word1);
  word_setstate(word1, setstate);
}

void update_pixel_state(word_map *pm, qlock_time qt) {
  printf("update pixel state");
  set_minute_pixels(pm, qt);
}

void sweep_changes(word_map *m) {
  for (int wi = 0; wi < m->size; wi++) {
    word *w = &(m->values[wi]);
    for (int pi = 0; pi < w->size; pi++) {
      pixel *p = &(w->pixels[pi]);

      if (p->change) {
        printf("CHANGE %d to %d\n", p->led_id, p->state);
        p->change = false;
      }
    }
  }
}

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
  printf("Start application with parameters: \n");
  printf("   rotation: %d\n", rot);

  ledgrid g = grid_init();
  grid_print(&g);

  word_map map = word_map_init();
  words_init(&map);

  for (int i = 0; i < map.size; i++) {
    grid_word_lookup(&g, &map.values[i]);
  }

  for (int i = 0; i < map.size; i++) {
    grid_rotate_word(&g, &map.values[i], rot);
  }

  while (1) {
    sleep(1);
    printf("tick tack ...\n");
    qlock_time qt = get_time();
    qlocktime_print(&qt);
    update_pixel_state(&map, qt);
    sweep_changes(&map);
  }
}

void words_init(word_map *map) {
  word_map_add(map, W_5, word_init(3, (int[]){13, 14, 15}));
  word_map_add(map, W_10, word_init(4, (int[]){40, 41, 42, 43}));
}

word word_init(uint size, const int *ids) {
  if (size > MAX_WORD_LENGTH) {
    return (word){0};
  }
  word w;
  int i;
  for (i = 0; i < size; i++) {
    pixel p = {0};
    p.led_id = ids[i];
    p.row_ind = -1;
    p.col_ind = -1;
    w.pixels[i] = p;
  }
  w.size = i;
  return w;
}

int word_initp(word *w, uint size, const int *ids) {
  // Initializes the word with the ids, sets indices to -1 since
  // they have not been found yet (in the grid)
  if (size > MAX_WORD_LENGTH) {
    return -1;
  }
  int i;
  for (i = 0; i < size; i++) {
    pixel p = {0};
    p.col_ind = -1;
    p.row_ind = -1;
    p.led_id = ids[i];
    w->pixels[i] = p;
  }
  w->size = i;
  return w->size;
}

void word_print(word *w) {
  printf("Word ids: [");
  for (int i = 0; i < w->size; i++) {
    printf(" %d", w->pixels[i].led_id);
  }
  printf("]\n");
}

void word_setstate(word *w, bool state) {
  for (int i = 0; i < w->size; i++) {
    w->pixels[i].state = state;
    w->pixels[i].change = true;
  }
}

ledgrid grid_init() {
  ledgrid g = {0};
  for (int j = 0; j < GRID_SIZE; j++) {
    for (int i = 0; i < GRID_SIZE; i++) {
      g.arr[j][i] = -1;
    }
  }

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
      if (num < 0) {
        printf(" %d ", g->arr[j][i]);
      } else if (num < 10) {
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
  // Based on the roated row/col indices, change the led_ids of the
  // corresponding word's pixels.
  for (int pind = 0; pind < w->size; pind++) {
    pixel *pp = &w->pixels[pind];
    if ((*pp).row_ind < 0 || (*pp).col_ind < 0) {
      return false;
    }

    int pid_rot = -1;

    switch (rot) {
    case ROT_0:
      return true;
    case ROT_90:
      // i=SIZE - j | j=i
      pid_rot = g->arr[(*pp).row_ind][GRID_SIZE - 1 - (*pp).col_ind];
      break;
    case ROT_180:
      // i=SIZE-1 | j=SIZE-j
      pid_rot =
          g->arr[GRID_SIZE - 1 - (*pp).col_ind][GRID_SIZE - 1 - (*pp).row_ind];
      break;
    case ROT_270:
      // i=j | j=SIZE-i
      pid_rot = g->arr[GRID_SIZE - 1 - (*pp).row_ind][(*pp).col_ind];
      break;
    }

    (*pp).led_id = pid_rot;
  }
  return true;
}

int grid_word_lookup(const ledgrid *g, word *w) {
  // Iterates over the grid to find the indices of eaech word pixel
  // The resulting indices (row, column) are then stored in word struct.

  int word_ind = 0;

  int fj = -1;
  int fi = -1;

  int done = 0;

  while (word_ind < w->size) {
    uint pixel_id = w->pixels[word_ind].led_id;
    for (int j = 0; j < GRID_SIZE && !done; j++) {
      for (int i = 0; i < GRID_SIZE; i++) {

        int candidate_id = g->arr[j][i];
        if (candidate_id == pixel_id) {
          // Found i,j indices for pixel id
          fj = j;
          fi = i;
          printf("Found pixel id: %d at (i=%d / j=%d)\n", candidate_id, fi, fj);
          w->pixels[word_ind].row_ind = fi;
          w->pixels[word_ind].col_ind = fj;
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
  return word_ind;
}

word_map word_map_init() {
  word_map m = {0};
  for (int i = 0; i < NUM_WORDS; i++) {
    m.keys[i] = W_INVALID;
  }
  return m;
}

bool word_map_add(word_map *m, enum WORD_DEFS key, const word w) {
  // check key does not exist
  for (int i = 0; i < NUM_WORDS; i++) {
    if (key == m->keys[i]) {
      printf("Key %d already exists!\n", key);
      return false;
    }
  }
  m->keys[m->size] = key;
  m->values[m->size] = w;
  m->size++;
  return true;
}

int word_map_get(word_map *m, enum WORD_DEFS key, word **out) {
  for (int i = 0; i < m->size; i++) {
    if (key == m->keys[i]) {
      *out = &m->values[i];
      return i;
    }
  }
  *out = NULL;
  return -1;
}

word *word_map_getp(word_map *m, enum WORD_DEFS key) {
  word *w;
  word_map_get(m, key, &w);
  return w;
}
