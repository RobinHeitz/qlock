#include "hardware/pio.h"
#include "pico/stdlib.h"
#include "ws2812.pio.h"
#include <cstdint>
#include <pico/assert.h>
#include <pico/error.h>
#include <pico/time.h>
#include <stdbool.h>
#include <stdio.h>

#include "ledcontroller.hpp"

constexpr uint8_t LED_PIN_WORDS = 0;
constexpr uint8_t LED_PIN_MINS = 1;

int main() {
  stdio_init_all();
  setup_default_uart();

  // Init of PIO program
  PIO pio_words, pio_mins;
  uint sm_words, sm_mins;
  uint offset_words, offset_mins;
  bool success = pio_claim_free_sm_and_add_program_for_gpio_range(
      &ws2812_program, &pio_words, &sm_words, &offset_words, LED_PIN_WORDS, 1,
      true);

  success = pio_claim_free_sm_and_add_program_for_gpio_range(
      &ws2812_program, &pio_mins, &sm_mins, &offset_mins, LED_PIN_MINS, 1,
      true);

  hard_assert(success);
  ws2812_program_init2(pio_words, sm_words, offset_words, LED_PIN_WORDS,
                       WS2812_FREQ_HZ);

  ws2812_program_init2(pio_mins, sm_mins, offset_mins, LED_PIN_MINS,
                       WS2812_FREQ_HZ);

  // Config is read from memory, can be changed through webserver
  // config site
  // QlockConfig conf = read_config_from_memory();

  QlockConfig config{
      .brightness = 123,
      .rot = Rotation::r0,
  };

  QlockController ctrl(config);

  // Setup words and data structures needed for the program

  ///////////////////////////////
  /// Actually start the loop ///
  ///////////////////////////////

  while (getchar_timeout_us(0) == PICO_ERROR_TIMEOUT) {
    ctrl.qlock();
    auto mins = ctrl.buffer_mins();
    auto words = ctrl.buffer_mins();

    for (const auto &b : mins) {
      pio_sm_put_blocking(pio_mins, sm_mins, b << 8);
    }
    for (const auto &b : words) {
      pio_sm_put_blocking(pio_words, sm_words, b << 8);
    }

    sleep_ms(1000);
  }

  pio_remove_program_and_unclaim_sm(&ws2812_program, pio_words, sm_words,
                                    offset_words);
}
