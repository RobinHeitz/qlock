#ifndef LED_CONTROLLER_HPP
#define LED_CONTROLLER_HPP

// #include "hardware/pio.h"
// #include "pico/stdlib.h"
#include <array>
#include <cstdint>
#include <span>

constexpr uint8_t DATA_LED_PIN = 0;
constexpr uint32_t WS2812_FREQ_HZ = 800000; // 1.25us per cycle

constexpr uint8_t GRID_SIZE = 12; // Grid of pixels (exc. minute dots)
constexpr uint8_t WORD_COUNT = 23;
constexpr uint8_t MAX_WORD_LENGTH = 10;

namespace Words {

constexpr size_t IT_IS = 0;
constexpr size_t THREE_QUARTER = 1;
constexpr size_t TWENTY = 2;
constexpr size_t QUARTER = 3;
constexpr size_t BEFORE = 4;
constexpr size_t AFTER = 5;
constexpr size_t GOOD_NIGHT = 6;
constexpr size_t GOOD_MORNING = 7;
constexpr size_t HALF = 8;
constexpr size_t PERSONAL_NAME = 9;
constexpr size_t ONE = 10;
constexpr size_t ONE_O_CLOCK = 11;
constexpr size_t TWO = 12;
constexpr size_t THREE = 13;
constexpr size_t FOUR = 14;
constexpr size_t FIVE = 15;
constexpr size_t SIX = 16;
constexpr size_t SEVEN = 17;
constexpr size_t EIGHT = 18;
constexpr size_t NINE = 19;
constexpr size_t TEN = 20;
constexpr size_t ELEVEN = 21;
constexpr size_t TWELVE = 22;

} // namespace Words

typedef struct WordDef {
  uint8_t length;
  uint8_t pixels[MAX_WORD_LENGTH];
} WordDef;

enum class Rotation : uint8_t { r0 = 0, r90 = 1, r180 = 2, r270 = 3 };

typedef struct PixelColor {
  uint8_t red;
  uint8_t green;
  uint8_t blue;
} PixelColor;

typedef struct QlockConfig {
  uint8_t brightness;
  PixelColor pixCol;
  Rotation rot;
} QlockConfig;

typedef struct QlockTime {
  int month; // 1-12
  int day;   // 1-31
  bool weekend;
  int hour; // 0-23
  int min;  // 0-59
  int sec;  // 0-60;
} QlockTime;

uint32_t to_grb(const PixelColor &pc);
// static void put_pixel(PIO pio, uint8_t sm, uint32_t pixel_grb);
static uint32_t urgb_u32(uint8_t r, uint8_t g, uint8_t b);

class QlockController {
public:
  QlockController(const QlockConfig &config);
  QlockController(QlockController &&) = default;
  QlockController(const QlockController &) = default;
  QlockController &operator=(QlockController &&) = default;
  QlockController &operator=(const QlockController &) = default;
  ~QlockController();

  // Frequenty called method
  void qlock();

private:
  std::array<WordDef, WORD_COUNT> words;
  uint8_t cur_min = -1;
  std::array<uint32_t, 4> data_mins;
  std::array<uint32_t, GRID_SIZE * GRID_SIZE> data_words;

  void init_word_defs();
  std::array<uint8_t, GRID_SIZE * GRID_SIZE>
  rotated_pixel_indices(Rotation rot);
  void apply_rotation(std::span<uint8_t, GRID_SIZE * GRID_SIZE> indices);

  inline void print_grid(uint8_t ids[GRID_SIZE][GRID_SIZE]) {
    // Printing stuff
    for (int j = 0; j < GRID_SIZE; j++) {
      for (int i = 0; i < GRID_SIZE; i++) {
        uint8_t num = ids[j][i];
        if (num < 10) {
          printf("  %d ", ids[j][i]);
        } else if (num < 100) {
          printf(" %d ", ids[j][i]);
        } else {
          printf("%d ", ids[j][i]);
        }
      }
      printf("\n");
    }
  }

  void write_to_pixels();
  void set_minute_pixels(uint8_t);
  QlockTime get_time();
};

#endif // !LED_CONTROLLER_HPP
