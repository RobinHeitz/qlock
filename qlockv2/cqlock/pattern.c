#include "stdbool.h"
#include "stdint.h"
#include "stdio.h"
#include <assert.h>
#define URGB_U32(r, g, b)                                                      \
  (((uint32_t)(g) << 16) | ((uint32_t)(r) << 8) | (uint32_t)(b))

#define NUM_PCBS_IN_ROW 4
#define NUM_LEDS_ON_PCB 9
#define WORD_GRID_LEN (NUM_PCBS_IN_ROW * 3)
#define NUM_WORD_LEDS (WORD_GRID_LEN * WORD_GRID_LEN)

typedef struct leds {
  uint8_t ids[NUM_WORD_LEDS];
  uint32_t colors[NUM_WORD_LEDS];
} qlock_leds;

void qlock_leds_init_row_l2r(qlock_leds *l, int row, int pcb_row,
                             bool pcb_order_rev) {
  assert(row <= 2);
  assert(pcb_row <= 3);

  int j = 0;
  int pcb_col_offset = -1;

  // offset of a row within same pcb:
  // 0 1 2 vs 6 7 8
  int row_offset = row * 3;

  int start_index = WORD_GRID_LEN * (row + pcb_row * 3);
  for (int i = 0; i < WORD_GRID_LEN; i++) {
    j = i % 3;
    if (j == 0) {
      pcb_col_offset = pcb_col_offset + 1;
    }

    int index = i + start_index;
    // reverse the row order if it is pcb row with inversed order
    index += (pcb_order_rev && (row == 2)) ? 2 * WORD_GRID_LEN : 0;
    index += (pcb_order_rev && (row == 0)) ? -2 * WORD_GRID_LEN : 0;

    int value = j + pcb_col_offset * NUM_LEDS_ON_PCB + row_offset +
                WORD_GRID_LEN * 3 * pcb_row;

    if (pcb_order_rev) {
      l->ids[2 * start_index - 1 + WORD_GRID_LEN - index] = value;
    } else {
      l->ids[index] = value;
    }
  }
}

void qlock_leds_init_row_r2l(qlock_leds *l, int row, int pcb_row,
                             bool pcb_order_rev) {
  assert(row <= 2);
  assert(pcb_row <= 3);

  int j = 0;
  int pcb_col_offset = -1;

  // offset of a row within same pcb:
  // 0 1 2 vs 6 7 8
  int row_offset = row * 3;

  int start_index = WORD_GRID_LEN * (row + pcb_row * 3);
  for (int i = 0; i < WORD_GRID_LEN; i++) {
    j = i % 3;
    if (j == 0) {
      pcb_col_offset = pcb_col_offset + 1;
    }

    int index = i + start_index;
    int value = 2 - j + pcb_col_offset * NUM_LEDS_ON_PCB + row_offset +
                WORD_GRID_LEN * 3 * pcb_row;

    if (pcb_order_rev) {
      l->ids[2 * start_index - 1 + WORD_GRID_LEN - index] = value;
    } else {
      l->ids[index] = value;
    }
  }
}

void qlock_leds_print_row(const qlock_leds *l, int row, int pcb_row) {
  printf("pcb_row=%d row %d:   ", pcb_row, row);
  int index_offset = WORD_GRID_LEN * (row + 3 * pcb_row);
  for (int i = 0; i < WORD_GRID_LEN; i++) {
    if (i % 3 == 0) {
      printf("|");
    }
    printf("%3d ", l->ids[i + index_offset]);
  }
  printf("\n");
}

void qlock_leds_print_rows(const qlock_leds *l) {
  for (int pcb_row = 0; pcb_row < NUM_PCBS_IN_ROW; pcb_row++) {
    printf("                    ");
    for (int j = 0; j < NUM_PCBS_IN_ROW; j++) {
      printf("------------ ");
    }
    printf("\n");
    for (int row = 0; row < 3; row++) {
      qlock_leds_print_row(l, row, pcb_row);
    }
  }
}

int main() {
  qlock_leds l = {0};

  /* qlock_leds_init_row_l2r(&l, 0, 0, false); */
  /**/
  /* qlock_leds_init_row_l2r(&l, 0, 1, true); */
  /* qlock_leds_init_row_l2r(&l, 2, 1, true); */

  for (int i = 0; i < NUM_PCBS_IN_ROW; i++) {
    qlock_leds_init_row_r2l(&l, 1, i, i % 2);
  }

  for (int i = 0; i < NUM_PCBS_IN_ROW; i++) {
    if (i % 2 == 0) {
      qlock_leds_init_row_l2r(&l, 0, i, i % 2);
      qlock_leds_init_row_l2r(&l, 2, i, i % 2);

    } else {
      qlock_leds_init_row_l2r(&l, 2, i, i % 2);
      qlock_leds_init_row_l2r(&l, 0, i, i % 2);
    }
  }

  /* qlock_leds_init_row_r2l(&l, 1, 0, false); */
  /* qlock_leds_init_row_r2l(&l, 1, 1, true); */
  /* qlock_leds_init_row_r2l(&l, 1, 2, false); */
  /* qlock_leds_init_row_r2l(&l, 1, 3, true); */

  /* qlock_leds_init_row_l2r(&l, 0, 1, true); */
  /* qlock_leds_init_row_l2r(&l, 2, 0); */
  /* qlock_leds_init_row_l2r(&l, 0, 2); */
  /* qlock_leds_init_row_l2r(&l, 2, 2); */
  qlock_leds_print_rows(&l);
}
