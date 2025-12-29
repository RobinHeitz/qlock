#include "hardware/pio.h"
#include "pico/stdlib.h"
#include <pico/assert.h>
#include <pico/error.h>
#include <pico/time.h>
#include <stdio.h>

#include "ws2812.pio.h"

#define DATA_LED_PIN 0

// WS2812 = 800kHz frequency
//

typedef struct {
  uint8_t red;
  uint8_t green;
  uint8_t blue;
} pixelColor;

pixelColor make_red() { return pixelColor{0xFF, 0, 0}; }
pixelColor make_green() { return pixelColor{0, 0xFF, 0}; }
pixelColor make_blue() { return pixelColor{0, 0, 0xFF}; }

uint32_t to_grb(const pixelColor &pc) {
  uint32_t grb =
      (pc.green & 0xFF) << 16 | (pc.red & 0xFF) << 8 | (pc.blue & 0xFF);
  return grb << 8;
}

static inline void put_pixel(PIO pio, uint sm, uint32_t pixel_grb) {
  pio_sm_put_blocking(pio, sm, pixel_grb << 8);
}

static inline uint32_t urgb_u32(uint8_t r, uint8_t g, uint8_t b) {
  return ((uint32_t)(r) << 8) | ((uint32_t)(g) << 16) | (uint32_t)(b);
}

int main() {
  stdio_init_all();

  PIO pio;
  uint sm;
  uint offset;
  setup_default_uart();

  bool success = pio_claim_free_sm_and_add_program_for_gpio_range(
      &ws2812_program, &pio, &sm, &offset, DATA_LED_PIN, 1, true);

  hard_assert(success);

  printf("Using gpio %d\n", DATA_LED_PIN);

  // ws2812_program_init(pio, sm, offset, DATA_LED_PIN);
  ws2812_program_init2(pio, sm, offset, DATA_LED_PIN, 800000);

  // auto pix1 = make_red();
  // auto pix2 = make_green();
  // auto pix3 = make_blue();

  bool on = false;
  int color = 0;
  while (getchar_timeout_us(0) == PICO_ERROR_TIMEOUT) {
    uint32_t data;

    if (on) {

      if (color == 0) {
        data = urgb_u32(0xff, 0x0, 0x0);
      } else if (color == 1) {
        data = urgb_u32(0x0, 0xff, 0x0);
      } else {
        data = urgb_u32(0x0, 0x0, 0xff);
      }

    } else {
      data = urgb_u32(0x0, 0x0, 0x0);
      data++;
      data = data % 3;
    }

    for (int i = 0; i < 9; i++) {
      put_pixel(pio, sm, data);
    }

    // Blink
    // pio_sm_put_blocking(pio, sm, to_grb(pix1));
    // pio_sm_put_blocking(pio, sm, to_grb(pix2));
    // pio_sm_put_blocking(pio, sm, to_grb(pix3));

    on = !on;
    sleep_ms(1000);

    // pio_sm_put_blocking(pio, sm, 0);
    // pio_sm_put_blocking(pio, sm, 0);
    // pio_sm_put_blocking(pio, sm, 0);
    // sleep_ms(500);
  }

  pio_remove_program_and_unclaim_sm(&ws2812_program, pio, sm, offset);
}
