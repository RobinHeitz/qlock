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
  words[Words::FIVE_1] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::FIVE_2] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::SIX] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::SEVEN] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::EIGHT] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::NINE] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::TEN_1] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
  words[Words::TEN_2] = WordDef{.length = 5, .pixels = {0, 1, 2, 3}};
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

void QlockController::set_clock_hour_words(uint8_t hour, uint8_t mins) {
  // just setting hour words. If min >= 25, go to next hour
  // 'Es ist 5 vor halb 6' =/= hour:5

  uint8_t hour12;
  if (mins >= 25) {
    hour12 = (hour + 1) % 12;
  } else {
    hour12 = hour % 12;
  }

  switch (hour12) {
  case 0:
    set_word_color(Words::TWELVE, 0xff, 0xff, 0xff);
    break;
  case 1:
    if (mins < 5) {
      set_word_color(Words::ONE_O_CLOCK, 0xff, 0xff, 0xff);
    } else {
      set_word_color(Words::ONE, 0xff, 0xff, 0xff);
    }
    break;
  case 2:
    set_word_color(Words::TWO, 0xff, 0xff, 0xff);
    break;
  case 3:
    set_word_color(Words::THREE, 0xff, 0xff, 0xff);
    break;
  case 4:
    set_word_color(Words::FOUR, 0xff, 0xff, 0xff);
    break;
  case 5:
    set_word_color(Words::FIVE_2, 0xff, 0xff, 0xff);
    break;
  case 6:
    set_word_color(Words::SIX, 0xff, 0xff, 0xff);
    break;
  case 7:
    set_word_color(Words::SEVEN, 0xff, 0xff, 0xff);
    break;
  case 8:
    set_word_color(Words::EIGHT, 0xff, 0xff, 0xff);
    break;
  case 9:
    set_word_color(Words::NINE, 0xff, 0xff, 0xff);
    break;
  case 10:
    set_word_color(Words::TEN_1, 0xff, 0xff, 0xff);
    break;
  case 11:
    set_word_color(Words::ELEVEN, 0xff, 0xff, 0xff);
    break;
  }
}

void QlockController::set_clock_words(uint8_t hour, uint8_t mins) {

  if ((mins >= 5) && (mins < 25)) {
    // 5..10..15..20 NACH 1/2/3
    uint8_t min_div = mins / 5;
    switch (min_div) {
    default:
      set_word_color(Words::AFTER, 0xff, 0xff, 0xff);
    case 1: // 5 (min) NACH
      set_word_color(Words::FIVE_1, 0xff, 0xff, 0xff);
      break;
    case 2: // 10 (min) NACH
      set_word_color(Words::TEN_1, 0xff, 0xff, 0xff);
      break;
    case 3: // 15 (min) NACH
      set_word_color(Words::QUARTER, 0xff, 0xff, 0xff);
      break;
    case 4: // 20 (min) NACH
      set_word_color(Words::TWENTY, 0xff, 0xff, 0xff);
      break;
    }
  } else if ((mins >= 25) && (mins < 30)) {
    // 5 VOR halb 6
    set_word_color(Words::FIVE_1, 0xff, 0xff, 0xff);
    set_word_color(Words::BEFORE, 0xff, 0xff, 0xff);
    set_word_color(Words::HALF, 0xff, 0xff, 0xff);
  } else if ((mins >= 30) && (mins < 35)) {
    // HALB 7
    set_word_color(Words::HALF, 0xff, 0xff, 0xff);

  } else if ((mins >= 35) && (mins < 40)) {
    // 5 NACH HALB 7
    set_word_color(Words::FIVE_1, 0xff, 0xff, 0xff);
    set_word_color(Words::AFTER, 0xff, 0xff, 0xff);
    set_word_color(Words::HALF, 0xff, 0xff, 0xff);
  } else if (mins >= 40) {
    // 20 VOR 8 || 15 VOR 8 || 10 VOR 8 || 5 VOR 8
    uint8_t mins_div = mins / 5;
    switch (mins_div) {
    default:
      set_word_color(Words::BEFORE, 0xff, 0xff, 0xff);
    case 8: // [40-45)
      set_word_color(Words::TWENTY, 0xff, 0xff, 0xff);
      break;
    case 9: // [45-50)
      set_word_color(Words::QUARTER, 0xff, 0xff, 0xff);
      break;
    case 10: // [50-55)
      set_word_color(Words::TEN_1, 0xff, 0xff, 0xff);
      break;
    case 11: // [55-60)
      set_word_color(Words::FIVE_1, 0xff, 0xff, 0xff);
      break;
    }
  }
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

void QlockController::set_word_color(uint8_t wordId, uint8_t r, uint8_t g,
                                     uint8_t b) {
  WordDef word = words[wordId];
  for (int i = 0; i < word.length; i++) {
    auto pixel_id = word.pixels[i];
    data_words[pixel_id] = urgb_u32(r, g, b);
  }
}

void QlockController::qlock() {
  // gather time
  QlockTime time = this->get_time();
  printf("%d:%d:%d", time.hour, time.min, time.sec);

  if (time.min == cur_min) {
    return;
  }
  // update data_mins
  std::cout << "minutes changed, set new pixels now." << std::endl;
  cur_min = time.min;
  set_minute_pixels(cur_min);

  // clear all words data
  for (auto &b : data_words) {
    b = 0;
  }
  set_word_color(Words::IT_IS, 0xff, 0xff, 0xff);
  set_clock_words(time.hour, time.min);
  set_clock_hour_words(time.hour, time.min);
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

std::span<const uint32_t> QlockController::buffer_mins() const {
  return data_mins;
}
std::span<const uint32_t> QlockController::buffer_words() const {
  return data_words;
}
