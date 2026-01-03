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

int main() {
  stdio_init_all();
  setup_default_uart();

  // Init of PIO program
  PIO pio;
  uint sm;
  uint offset;
  bool success = pio_claim_free_sm_and_add_program_for_gpio_range(
      &ws2812_program, &pio, &sm, &offset, DATA_LED_PIN, 1, true);

  hard_assert(success);
  printf("Using gpio %d\n", DATA_LED_PIN);
  ws2812_program_init2(pio, sm, offset, DATA_LED_PIN, WS2812_FREQ_HZ);

  // Config is read from memory, can be changed through webserver
  // config site
  // QlockConfig conf = read_config_from_memory();

  // Setup words and data structures needed for the program

  ///////////////////////////////
  /// Actually start the loop ///
  ///////////////////////////////

  bool on = false;

  while (getchar_timeout_us(0) == PICO_ERROR_TIMEOUT) {
    uint32_t data;

    if (on) {
      // data = urgb_u32(0x00, 0x00, 0xFF);

    } else {
      // data = urgb_u32(0x0, 0x0, 0x0);
    }

    for (int i = 0; i < 9; i++) {
      // put_pixel(pio, sm, data);
    }
    on = !on;
    sleep_ms(1000);
  }

  pio_remove_program_and_unclaim_sm(&ws2812_program, pio, sm, offset);
}
