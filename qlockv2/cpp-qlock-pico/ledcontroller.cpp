#include "ledcontroller.hpp"
#include <cassert>
#include <chrono>
#include <cstdio>
#include <iostream>
#include <stdlib.h>
#include <thread>
#include <time.h>

// shifts colors into 3 LSB.
uint32_t to_grb(const PixelColor &pc) {
  uint32_t grb =
      (uint32_t)pc.green << 16 | (uint32_t)pc.red << 8 | (uint32_t)pc.blue;
  return grb;
}

// puts data into PIO (blocking). 24 bits are read before auto-repulled.
// shift 24bits from LSB to MSB (<<8).
// static void put_pixel(PIO pio, uint8_t sm, uint32_t pixel_grb) {
//   pio_sm_put_blocking(pio, sm, pixel_grb << 8);
// }

// shifts colors into 3 LSB.
static uint32_t urgb_u32(uint8_t r, uint8_t g, uint8_t b) {
  return ((uint32_t)(r) << 8) | ((uint32_t)(g) << 16) | (uint32_t)(b);
}

QlockController::QlockController(const QlockConfig &config) {
  cur_min = -1;
  init_word_defs();
  auto indices = rotated_pixel_indices(config.rot);
  apply_rotation(indices);
}

QlockController::~QlockController() {}

void QlockController::init_word_defs() {
  words[Words::IT_IS] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::THREE_QUARTER] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::TWENTY] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::QUARTER] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::BEFORE] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::AFTER] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::GOOD_NIGHT] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::GOOD_MORNING] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::HALF] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::PERSONAL_NAME] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::ONE] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::ONE_O_CLOCK] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::TWO] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::THREE] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::FOUR] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::FIVE] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::SIX] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::SEVEN] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::EIGHT] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::NINE] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::TEN] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::ELEVEN] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::TWELVE] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
}

// Indices are based on rotation (config),
// therefore indices[i] contains new index for i (after rotation)
void QlockController::apply_rotation(
    std::span<uint8_t, GRID_SIZE * GRID_SIZE> indices) {

  for (int windex = 0; windex < WORD_COUNT; windex++) {
    auto w = &words[windex];
    printf("Got word #%d (length=%d):   ", windex, w->length);
    for (int i = 0; i < w->length; i++) {
      uint8_t indexold = w->pixels[i];
      printf("%d.", w->pixels[i]);
      w->pixels[i] = indices[indexold];
    }
    printf("\n");
  }
}

// rotated by creating grid of indizes with reverse access order
// (GRID_SIZE - 1 - <index>) based on rotation value.
// Then flattened, such that accessing the updated pixel index
// is simply lookup of the array.
std::array<uint8_t, GRID_SIZE * GRID_SIZE>
QlockController::rotated_pixel_indices(Rotation rot) {

  uint8_t ids[GRID_SIZE][GRID_SIZE] = {0};
  bool i_inv = false;
  for (int j = 0; j < GRID_SIZE; j++) {
    for (int i = 0; i < GRID_SIZE; i++) {
      if (i_inv == true) {
        ids[j][GRID_SIZE - 1 - i] = GRID_SIZE * j + i;
      } else {
        ids[j][i] = GRID_SIZE * j + i;
      }
    }
    i_inv = !i_inv;
  }

  // uint8_t flat_ids[GRID_SIZE * GRID_SIZE];
  uint8_t rotated[GRID_SIZE][GRID_SIZE] = {0};

  switch (rot) {
  case Rotation::r0:
    for (int j = 0; j < GRID_SIZE; j++) {
      for (int i = 0; i < GRID_SIZE; i++) {
        rotated[j][i] = ids[j][i];
      }
    }

    break;
  case Rotation::r90:
    for (int j = 0; j < GRID_SIZE; j++) {
      for (int i = 0; i < GRID_SIZE; i++) {
        rotated[j][i] = ids[GRID_SIZE - 1 - i][j];
      }
    }
    break;
  case Rotation::r180:
    for (int j = 0; j < GRID_SIZE; j++) {
      for (int i = 0; i < GRID_SIZE; i++) {
        rotated[j][i] = ids[GRID_SIZE - 1 - j][GRID_SIZE - 1 - i];
      }
    }
    break;
  case Rotation::r270:
    for (int j = 0; j < GRID_SIZE; j++) {
      for (int i = 0; i < GRID_SIZE; i++) {
        rotated[j][i] = ids[i][GRID_SIZE - 1 - j];
      }
    }
    break;
  };

  std::array<uint8_t, GRID_SIZE * GRID_SIZE> flattened;
  i_inv = false;
  uint8_t index = 0;
  for (int j = 0; j < GRID_SIZE; j++) {
    for (int i = 0; i < GRID_SIZE; i++) {
      if (i_inv == true) {
        flattened[index++] = rotated[j][GRID_SIZE - 1 - i];
      } else {
        flattened[index++] = rotated[j][i];
      }
    }
    i_inv = !i_inv;
  }
  assert(index == GRID_SIZE * GRID_SIZE && "Flatten did not worked.");

  return flattened;
}

void QlockController::set_minute_pixels(uint8_t min) {
  uint8_t mins_to_set = min % 5;
  switch (mins_to_set) {
  case 4:
    data_mins[3] = urgb_u32(60, 61, 62);
  case 3:
    data_mins[2] = urgb_u32(50, 51, 52);
  case 2:
    data_mins[1] = urgb_u32(200, 201, 202);
  case 1:
    data_mins[0] = urgb_u32(100, 101, 102);
    break;
  default:
    for (auto &b : data_mins) {
      b = urgb_u32(0, 0, 0);
    }
    break;
  }
  int i = 0;
  for (const auto &p : data_mins) {
    printf("%d ", i++);
    printf("red=%u | green=%u | blue=%u\n", (p >> 8) & 0xff, (p >> 16) & 0xff,
           p & 0xff);
  }
}

void QlockController::qlock() {
  // gather time
  QlockTime time = this->get_time();
  if (time.min == cur_min) {
    return;
  }

  std::cout << "minutes changed, set new pixels now." << std::endl;

  cur_min = time.min;
  this->set_minute_pixels(cur_min);

  // make changes to array

  // write array content to pio
  this->write_to_pixels();
}

QlockTime QlockController::get_time() {
  time_t rawtime;
  struct tm *timeinfo;
  time(&rawtime);
  timeinfo = localtime(&rawtime);

  QlockTime qt;
  qt.month = timeinfo->tm_mon + 1;
  qt.day = timeinfo->tm_mday;
  int w_day = timeinfo->tm_wday;
  qt.weekend = w_day == 6 || w_day == 0;
  qt.hour = timeinfo->tm_hour;
  qt.min = timeinfo->tm_min;
  qt.sec = timeinfo->tm_sec;
  return qt;
}

void QlockController::write_to_pixels() {}
