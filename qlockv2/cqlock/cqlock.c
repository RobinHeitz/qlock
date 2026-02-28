#include "hardware/clocks.h"
#include "hardware/i2c.h"
#include "hardware/pio.h"
#include "hardware/timer.h"
#include "hardware/uart.h"
#include "pico/cyw43_arch.h"
#include "pico/stdlib.h"
#include <hardware/gpio.h>
#include <stdio.h>
#include <stdlib.h>

#include "led.pio.h"

#define WS2812_FREQ 800 * 1000

#define WS2812_WORD_PIN 1
#define NUM_LEDS 9 * 1
#define NUM_COLORS 8

#define WS2812_MIN_PIN 0 // GPIO 0 for the 4 minute indicating pixels

// i2c to communicate with DS3231 RTC
#define DS3231_ADDR 0x68
#define EEPROM_ADDR 0x57
#define SDA_PIN 16
#define SCL_PIN 17

#define DS3231_BUF_LEN 7

uint8_t *ds3231_buf = NULL;

typedef struct qlock {
  uint8_t secs;
  uint8_t mins;
  uint8_t hours;
  uint8_t day;   // which day in week 1-7
  uint8_t date;  // 1-31
  uint8_t month; // 1-12
  uint16_t year; // 0-65535
} qlock;

typedef struct pio_conf {
  PIO pio;
  uint sm;
  uint offset;
} pio_conf;

static inline void ws2812_program_init(pio_conf *pio_conf, uint pin,
                                       float freq) {
  pio_gpio_init(pio_conf->pio, pin);
  pio_sm_set_consecutive_pindirs(pio_conf->pio, pio_conf->sm, pin, 1, true);

  pio_sm_config c = ws2812_program_get_default_config(pio_conf->offset);
  sm_config_set_sideset_pins(&c, pin);
  sm_config_set_out_shift(&c, false, true,
                          24); // shift left, autopull at 24 bits
  sm_config_set_fifo_join(&c, PIO_FIFO_JOIN_TX);

  int cycles_per_bit = ws2812_T1 + ws2812_T2 + ws2812_T3;
  float div = clock_get_hz(clk_sys) / (freq * cycles_per_bit);
  sm_config_set_clkdiv(&c, div);

  pio_sm_init(pio_conf->pio, pio_conf->sm, pio_conf->offset, &c);
  pio_sm_set_enabled(pio_conf->pio, pio_conf->sm, true);
}

// Send a single pixel (GRB format, shifted into upper 24 bits)
static inline void put_pixel(pio_conf *pio_conf, uint32_t grb) {
  pio_sm_put_blocking(pio_conf->pio, pio_conf->sm, grb << 8u);
}

// Convert RGB to the GRB format WS2812B expects
static inline uint32_t urgb_u32(uint8_t r, uint8_t g, uint8_t b) {
  return ((uint32_t)g << 16) | ((uint32_t)r << 8) | (uint32_t)b;
}

int64_t alarm_callback(alarm_id_t id, void *user_data) {
  // Put your timeout handler code in here
  return 0;
}

// UART defines
// By default the stdout UART is `uart0`, so we will use the second one
/* #define UART_ID uart1 */
/* #define BAUD_RATE 115200 */

// Use pins 4 and 5 for UART1
// Pins can be changed, see the GPIO function select table in the datasheet for
// information on GPIO assignments
/* #define UART_TX_PIN 4 */
/* #define UART_RX_PIN 5 */

// I2C reserves some addresses for special purposes. We exclude these from the
// scan. These are any addresses of the form 000 0xxx or 111 1xxx
bool reserved_addr(uint8_t addr) {
  return (addr & 0x78) == 0 || (addr & 0x78) == 0x78;
}

/* int i2c_write_blocking (i2c_inst_t *i2c, uint8_t addr, const uint8_t *src,
 * size_t len, bool nostop) */
/* int i2c_read_blocking (i2c_inst_t *i2c, uint8_t addr, uint8_t *dst, size_t
 * len, bool nostop) */

void read_EEMPROM() {
  printf("start reading eeprom\n");

  uint8_t *dst = malloc(10);
  int ret = i2c_read_blocking(i2c_default, EEPROM_ADDR, dst, 10, true);
  printf("ret = %d\n", ret);

  if (ret > 0) {
    printf("Reading data now: \n");
    for (int i = 0; i < ret; i++) {
      printf("  %d: %d \n", i, dst[i]);
    }
  }
  free(dst);
}

void qlock_print(const qlock *q) {
  char *day = NULL;
  switch (q->day) {
  case 1:
    day = "Mon";
    break;
  case 2:
    day = "Tue";
    break;
  case 3:
    day = "Wed";
    break;
  case 4:
    day = "Thu";
    break;
  case 5:
    day = "Fri";
    break;
  case 6:
    day = "Sat";
    break;
  case 7:
    day = "Sun";
    break;
  default:
    day = "";
    break;
  }

  char *month = NULL;
  switch (q->month) {
  case 1:
    month = "Jan";
    break;
  case 2:
    month = "Feb";
    break;
  case 3:
    month = "Mar";
    break;
  case 4:
    month = "Apr";
    break;
  case 5:
    month = "May";
    break;
  case 6:
    month = "Jun";
    break;
  case 7:
    month = "Jul";
    break;
  case 8:
    month = "Aug";
    break;
  case 9:
    month = "Sep";
    break;
  case 10:
    month = "Oct";
    break;
  case 11:
    month = "Nov";
    break;
  case 12:
    month = "Dec";
    break;
  default:
    month = "";
    break;
  }

  printf("-------------------------\n");
  printf("%.*s, %u. %.*s   %02u:%02u:%02u\n", 3, day, q->date, 3, month,
         q->hours, q->mins, q->secs);
}

int qlock_set_ds3231(const qlock *q) {
  uint8_t data[8];
  data[0] = 0x00; // starting register addr
  data[1] = (q->secs % 10) | ((q->secs / 10) << 4);
  data[2] = (q->mins / 10) << 4 | (q->mins % 10);
  data[3] = (q->hours / 10) << 4 | (q->hours % 10);

  // set bit 6 to 0 for 24h format selection
  data[3] = data[3] & ((1 << 6) ^ 0xff);

  data[4] = q->day;
  data[5] = (q->date % 10) | ((q->date / 10) << 4);
  data[6] = (q->month % 10) | ((q->month / 10) << 4);

  uint8_t y = q->year % 100;
  data[7] = (y % 10) | ((y / 10) << 4);
  return i2c_write_blocking(i2c_default, DS3231_ADDR, data, 8, false);
}

void pio_setup(pio_conf *pio_mins, pio_conf *pio_words) {
  // PIO for commanding the words
  pio_words->pio = pio0;
  pio_words->sm = 0;
  pio_words->offset = pio_add_program(pio_words->pio, &ws2812_program);

  pio_mins->pio = pio1;
  pio_mins->sm = 0;
  pio_mins->offset = pio_add_program(pio_mins->pio, &ws2812_program);

  // PIO for commanding the 4 minute pixels
  /* PIO pio_min = pio1; */
  /* uint sm_min = 0; */
  /* uint offset_min = pio_add_program(pio_min, &ws2812_program); */

  ws2812_program_init(pio_words, WS2812_WORD_PIN, WS2812_FREQ);
  ws2812_program_init(pio_mins, WS2812_MIN_PIN, WS2812_FREQ);
}

int qlock_read(qlock *out) {
  if (ds3231_buf == NULL) {
    ds3231_buf = malloc(sizeof(uint8_t) * DS3231_BUF_LEN);
  }
  uint8_t reg = 0x00;
  i2c_write_blocking(i2c_default, DS3231_ADDR, &reg, 1, true);
  int ret = i2c_read_blocking(i2c_default, DS3231_ADDR, ds3231_buf,
                              DS3231_BUF_LEN, false);

  out->secs = (ds3231_buf[0] >> 4) * 10 + (ds3231_buf[0] & 0x0f);
  out->mins = (ds3231_buf[1] >> 4) * 10 + (ds3231_buf[1] & 0x0f);
  out->hours = ((ds3231_buf[2] >> 4) & 0x3) * 10 + (ds3231_buf[2] & 0x0f);
  out->day = ds3231_buf[3] & ((1 << 3) - 1);
  out->date = (ds3231_buf[4] & 0xf) + 10 * (ds3231_buf[4] >> 4);
  out->month = (ds3231_buf[5] & 0xf) + 10 * ((ds3231_buf[5] >> 4) & 0x1);
  return ret;
}

void i2c_setup() {
  printf("setting up i2c\n");

  // init i2c
  i2c_init(i2c_default, 100 * 1000);
  gpio_set_function(SDA_PIN, GPIO_FUNC_I2C);
  gpio_set_function(SCL_PIN, GPIO_FUNC_I2C);
  gpio_pull_up(SDA_PIN);
  gpio_pull_up(SCL_PIN);
}

void i2c_scan() {
  printf("---------\n");
  printf("Start scanning i2c device...\n");
  for (int addr = 0; addr < (1 << 7); ++addr) {
    if (addr % 16 == 0) {
      printf("%02x ", addr);
    }
    // Perform a 1-byte dummy read from the probe address. If a slave
    // acknowledges this address, the function returns the number of bytes
    // transferred. If the address byte is ignored, the function returns
    // -1.

    // Skip over any reserved addresses.
    int ret;
    uint8_t rxdata;
    if (reserved_addr(addr))
      ret = PICO_ERROR_GENERIC;
    else
      ret = i2c_read_blocking(i2c_default, addr, &rxdata, 1, false);

    printf(ret < 0 ? "." : "@");
    printf(addr % 16 == 15 ? "\n" : "  ");
  }
  printf("\n");
  printf("Finished scanning i2c\n");
  printf("---------\n");
}

int main() {
  stdio_init_all();

  pio_conf pio_mins = {0};
  pio_conf pio_words = {0};

  pio_setup(&pio_mins, &pio_words);

  i2c_setup();
  sleep_ms(2000);
  i2c_scan();
  sleep_ms(2000);

  // Setting qlock
  /* qlock qlock = {.secs = 40, */
  /*                .mins = 32, */
  /*                .hours = 13, */
  /*                .day = 6, */
  /*                .date = 28, */
  /*                .month = 2, */
  /*                .year = 2026}; */
  /**/
  /* qlock_print(&qlock); */
  /* qlock_set_ds3231(&qlock); */

  qlock out_qlock = {0};

  /* printf("Set qlock: %d\n", set_clock_ds3231()); */
  sleep_ms(1000);

  /* printf("-------\n"); */
  /* read_EEMPROM(); */
  /* printf("-------\n"); */

  // Initialise the Wi-Fi chip
  if (cyw43_arch_init()) {
    printf("Wi-Fi init failed\n");
    return -1;
  }

  // Timer example code - This example fires off the callback after 2000ms
  /* add_alarm_in_ms(2000, alarm_callback, NULL, false); */
  // For more examples of timer use see
  // https://github.com/raspberrypi/pico-examples/tree/master/timer

  // Enable wifi station
  /* cyw43_arch_enable_sta_mode(); */

  /* printf("Connecting to Wi-Fi...\n"); */
  /* if (cyw43_arch_wifi_connect_timeout_ms("Your Wi-Fi SSID", */
  /*                                        "Your Wi-Fi Password", */
  /*                                        CYW43_AUTH_WPA2_AES_PSK, 30000)) {
   */
  /*   printf("failed to connect.\n"); */
  /*   return 1; */
  /* } else { */
  /*   printf("Connected.\n"); */
  /*   // Read the ip address in a human readable way */
  /*   uint8_t *ip_address = (uint8_t *)&(cyw43_state.netif[0].ip_addr.addr); */
  /*   printf("IP address %d.%d.%d.%d\n", ip_address[0], ip_address[1], */
  /*          ip_address[2], ip_address[3]); */
  /* } */

  // Set up our UART
  /* uart_init(UART_ID, BAUD_RATE); */
  /* // Set the TX and RX pins by using the function select on the GPIO */
  /* // Set datasheet for more information on function select */
  /* gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART); */
  /* gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART); */
  /**/
  // Use some the various UART functions to send out data
  // In a default system, printf will also output via the default UART

  // Send out a string, with CR/LF conversions
  /* uart_puts(UART_ID, " Hello, UART!\n"); */

  // For more examples of UART use see
  // https://github.com/raspberrypi/pico-examples/tree/master/uart

  uint8_t index = 0;

  uint32_t colors[] = {
      urgb_u32(25, 0, 0),  // red
      urgb_u32(0, 25, 0),  // green
      urgb_u32(0, 0, 25),  // blue
      urgb_u32(25, 25, 0), // yellow
      urgb_u32(0, 25, 25), // cyan
      urgb_u32(25, 0, 25), // magenta
      urgb_u32(25, 12, 0), // orange
      urgb_u32(25, 25, 25) // white
  };

  /* uint32_t colors[] = { */
  /*     urgb_u32(255, 0, 0),    // red */
  /*     urgb_u32(0, 255, 0),    // green */
  /*     urgb_u32(0, 0, 255),    // blue */
  /*     urgb_u32(255, 255, 0),  // yellow */
  /*     urgb_u32(0, 255, 255),  // cyan */
  /*     urgb_u32(255, 0, 255),  // magenta */
  /*     urgb_u32(255, 128, 0),  // orange */
  /*     urgb_u32(255, 255, 255) // white */
  /* }; */

  uint32_t ledoff = 0;

  while (true) {

    for (int i = 0; i < NUM_LEDS; i++) {
      if (i == index) {
        put_pixel(&pio_mins, colors[i % NUM_COLORS]);
        put_pixel(&pio_words, colors[i % NUM_COLORS]);
      } else {
        put_pixel(&pio_mins, ledoff);
        put_pixel(&pio_words, ledoff);
      }
    }
    index = (index + 1) % NUM_LEDS;

    /* read_DS3231(); */
    qlock_read(&out_qlock);
    qlock_print(&out_qlock);
    sleep_ms(1000);
  }
}
