#include "hardware/clocks.h"
#include "hardware/i2c.h"
#include "hardware/pio.h"
#include "hardware/timer.h"
#include "hardware/uart.h"
#include "pico/cyw43_arch.h"
#include "pico/stdlib.h"
#include <assert.h>
#include <hardware/gpio.h>
#include <stdio.h>
#include <stdlib.h>

#include "led.pio.h"

#define WS2812_FREQ 800 * 1000
#define WS2812_MIN_PIN 0 // GPIO 0 for the 4 minute indicating pixels
#define WS2812_WORD_PIN 1
#define CONFIG_BUTTON_PIN 2

#define NUM_PCBS_IN_ROW 3
#define NUM_LEDS_ON_PCB 9
#define WORD_GRID_LEN (NUM_PCBS_IN_ROW * 3)
#define NUM_WORD_LEDS (WORD_GRID_LEN * WORD_GRID_LEN)

// i2c to communicate with DS3231 RTC
#define DS3231_BUF_LEN 7
#define DS3231_ADDR 0x68
#define EEPROM_ADDR 0x57
#define SDA_PIN 16
#define SCL_PIN 17

#define URGB_U32(r, g, b)                                                      \
  (((uint32_t)(g) << 16) | ((uint32_t)(r) << 8) | (uint32_t)(b))

typedef enum QlockState {
  QS_SETUP,
  QS_INIT,
  QS_TICK,
} QlockState;

typedef enum rotation {
  rot0 = 0,
  rot90 = 1,
  rot180 = 2,
  rot270 = 3,
} rotation;

typedef struct leds {
  uint8_t ids[NUM_WORD_LEDS];
  uint32_t colors[NUM_WORD_LEDS];
  rotation rot;
} qlock_leds;

typedef struct qlock_time {
  uint8_t secs;
  uint8_t mins;
  uint8_t hours;
  uint8_t day;   // which day in week 1-7
  uint8_t date;  // 1-31
  uint8_t month; // 1-12
  uint16_t year; // 0-65535
} qlock_time;

typedef struct pio_conf {
  PIO pio;
  uint sm;
  uint offset;
} pio_conf;

typedef enum colors {
  COLOR_OFF = 0,

  COLOR_RED = URGB_U32(255, 0, 0),
  COLOR_GREEN = URGB_U32(0, 0, 255),
  COLOR_BLUE = URGB_U32(0, 255, 0),

  COLOR_YELLOW = URGB_U32(255, 255, 0),
  COLOR_CYAN = URGB_U32(0, 255, 255),
  COLOR_MAGENTA = URGB_U32(255, 0, 255),

  COLOR_ORGANGE = URGB_U32(255, 128, 0),

  COLOR_WHITE = URGB_U32(255, 255, 255),
} colors;

///////////////////////////////////////
/////////// Global Vars ///////////////
///////////////////////////////////////

uint8_t *ds3231_buf = NULL;
QlockState qlockState = QS_INIT;

///////////////////////////////////////
///////////////////////////////////////
///////////////////////////////////////

// Send a single pixel (GRB format, shifted into upper 24 bits)
static inline void put_pixel(const pio_conf *pio_conf, uint32_t grb) {
  pio_sm_put_blocking(pio_conf->pio, pio_conf->sm, grb << 8u);
}

void qlock_leds_init_pcb_row(qlock_leds *l, int pcb_row) {
  // second row: ids increase 27

  int off = pcb_row * NUM_PCBS_IN_ROW * 3 * 3;

  l->ids[0 + off] = 0 + off;
  l->ids[1 + off] = 1 + off;
  l->ids[2 + off] = 2 + off;
  l->ids[9 + off] = 5 + off;
  l->ids[10 + off] = 4 + off;
  l->ids[11 + off] = 3 + off;
  l->ids[18 + off] = 6 + off;
  l->ids[19 + off] = 7 + off;
  l->ids[20 + off] = 8 + off;

  l->ids[3 + off] = 0 + 1 * 9 + off;
  l->ids[4 + off] = 1 + 1 * 9 + off;
  l->ids[5 + off] = 2 + 1 * 9 + off;
  l->ids[12 + off] = 5 + 1 * 9 + off;
  l->ids[13 + off] = 4 + 1 * 9 + off;
  l->ids[14 + off] = 3 + 1 * 9 + off;
  l->ids[21 + off] = 6 + 1 * 9 + off;
  l->ids[22 + off] = 7 + 1 * 9 + off;
  l->ids[23 + off] = 8 + 1 * 9 + off;
  l->ids[6 + off] = 0 + 2 * 9 + off;
  l->ids[7 + off] = 1 + 2 * 9 + off;
  l->ids[8 + off] = 2 + 2 * 9 + off;
  l->ids[15 + off] = 5 + 2 * 9 + off;
  l->ids[16 + off] = 4 + 2 * 9 + off;
  l->ids[17 + off] = 3 + 2 * 9 + off;
  l->ids[24 + off] = 6 + 2 * 9 + off;
  l->ids[25 + off] = 7 + 2 * 9 + off;
  l->ids[26 + off] = 8 + 2 * 9 + off;
}

// Establish a top-left origin, meaning that
// later on, words etc. can be defined by rows, columns
// reason: Easy to rotate such a thing
void qlock_leds_init(qlock_leds *l, rotation rot) {
  printf("led_map_init rot=%u\n", rot);
  l->rot = rot;

  qlock_leds_init_pcb_row(l, 0);
  qlock_leds_init_pcb_row(l, 1);
  qlock_leds_init_pcb_row(l, 2);

  // First pixel matrix pcb
  /* l->ids[0] = 0; */
  /* l->ids[1] = 1; */
  /* l->ids[2] = 2; */
  /* l->ids[9] = 5; */
  /* l->ids[10] = 4; */
  /* l->ids[11] = 3; */
  /* l->ids[18] = 6; */
  /* l->ids[19] = 7; */
  /* l->ids[20] = 8; */
  /**/
  /* l->ids[3] = 0 + 1 * 9; */
  /* l->ids[4] = 1 + 1 * 9; */
  /* l->ids[5] = 2 + 1 * 9; */
  /* l->ids[12] = 5 + 1 * 9; */
  /* l->ids[13] = 4 + 1 * 9; */
  /* l->ids[14] = 3 + 1 * 9; */
  /* l->ids[21] = 6 + 1 * 9; */
  /* l->ids[22] = 7 + 1 * 9; */
  /* l->ids[23] = 8 + 1 * 9; */
  /**/
  /* l->ids[6] = 0 + 2 * 9; */
  /* l->ids[7] = 1 + 2 * 9; */
  /* l->ids[8] = 2 + 2 * 9; */
  /* l->ids[15] = 5 + 2 * 9; */
  /* l->ids[16] = 4 + 2 * 9; */
  /* l->ids[17] = 3 + 2 * 9; */
  /* l->ids[24] = 6 + 2 * 9; */
  /* l->ids[25] = 7 + 2 * 9; */
  /* l->ids[26] = 8 + 2 * 9; */
}

void qlock_leds_reset_colors(qlock_leds *leds) {
  for (int i = 0; i < NUM_WORD_LEDS; i++) {
    leds->colors[i] = 0;
  }
}

void qlock_leds_set_color(qlock_leds *leds, uint8_t index, uint32_t color) {
  uint8_t pixel_number = leds->ids[index];
  leds->colors[pixel_number] = color;
}

void qlock_leds_sweep_words(const qlock_leds *leds, pio_conf *pio) {
  for (int i = 0; i < NUM_WORD_LEDS; i++) {
    uint8_t pixel_number = leds->ids[i];
    printf("  put color on pixel_number=%d color=%d\n", pixel_number,
           leds->colors[pixel_number]);
    put_pixel(pio, leds->colors[pixel_number]);
  }
}

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

void pio_setup(pio_conf *pio_mins, pio_conf *pio_words) {
  // PIO for commanding the words
  pio_words->pio = pio0;
  pio_words->sm = 0;
  pio_words->offset = pio_add_program(pio_words->pio, &ws2812_program);

  pio_mins->pio = pio1;
  pio_mins->sm = 0;
  pio_mins->offset = pio_add_program(pio_mins->pio, &ws2812_program);

  ws2812_program_init(pio_words, WS2812_WORD_PIN, WS2812_FREQ);
  ws2812_program_init(pio_mins, WS2812_MIN_PIN, WS2812_FREQ);
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

void qlock_print(const qlock_time *q) {
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

int qlock_write_ds3231(const qlock_time *q) {
  uint8_t data[1 + DS3231_BUF_LEN];
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

int qlock_read_ds3231(qlock_time *out) {
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

void pixel_render_spinning_clockwise(qlock_leds *leds) {
  const int extent_len = 2 * WORD_GRID_LEN + 2 * (WORD_GRID_LEN - 2); // 8
  const int divider = WORD_GRID_LEN - 1;                              // 2
  static int counter = 0;

  int segment_id = counter / divider;
  int seg_count = counter % divider;

  int led_id = -1;

  switch (segment_id) {
  case 0: // horizontal
    led_id = seg_count;
    break;
  case 1: // vertical
    led_id = seg_count * WORD_GRID_LEN + divider;
    break;
  case 2: // horizontal backwards
    led_id = WORD_GRID_LEN * WORD_GRID_LEN - 1 - seg_count;
    break;
  case 3: // vertical backwards
    led_id = (WORD_GRID_LEN - 1 - seg_count) * WORD_GRID_LEN;
    break;
  }
  /* printf("  led_id=%d | seg_count=%d | counter=%d\n", led_id, seg_count, */
  /* counter); */
  for (int i = 0; i < NUM_WORD_LEDS; i++) {
    uint8_t pixel_number = leds->ids[i];
    if (i == led_id) {
      qlock_leds_set_color(leds, pixel_number, COLOR_CYAN);
    } else {
      qlock_leds_set_color(leds, pixel_number, COLOR_OFF);
    }
  }
  counter = (counter + 1) % extent_len;
}

void pixel_render_serial(qlock_leds *leds) {
  static int counter = 0;

  for (int i = 0; i < NUM_WORD_LEDS; i++) {
    uint8_t pixel_number = leds->ids[i];
    /* qlock_leds_set_color(leds, pixel_number, col); */
    if (i == counter) {
      qlock_leds_set_color(leds, pixel_number, COLOR_RED);
      printf("  i=%d pixel_number=%d\n", i, pixel_number);
    } else {
      qlock_leds_set_color(leds, pixel_number, COLOR_OFF);
    }
  }
  counter = (counter + 1) % NUM_WORD_LEDS;
}

void set_minute_pixels(const qlock_time *q, const pio_conf *pio) {
  uint8_t mins = q->mins % 5;
  uint32_t min_buf[4] = {0};
  switch (mins) {
  case 4:
    min_buf[3] = COLOR_BLUE;
  case 3:
    min_buf[2] = COLOR_BLUE;
  case 2:
    min_buf[1] = COLOR_BLUE;
  case 1:
    min_buf[0] = COLOR_BLUE;
    break;
  }
  for (int i = 0; i < 4; i++) {
    put_pixel(pio, min_buf[i]);
  }
}

int main() {
  stdio_init_all();

  // Button setup
  /* gpio_set_function(CONFIG_BUTTON_PIN, GPIO_FUNC_GPCK); */
  /* gpio_pull_up(CONFIG_BUTTON_PIN); */

  QlockState qs = QS_SETUP;

  pio_conf pio_mins = {0};
  pio_conf pio_words = {0};

  pio_setup(&pio_mins, &pio_words);

  i2c_setup();
  sleep_ms(2000);

  /* i2c_scan(); */
  /* sleep_ms(2000); */

  qlock_time out_qlock = {0};
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

  qlock_leds *leds = malloc(sizeof(qlock_leds));
  qlock_leds_init(leds, rot0);
  qlock_leds_reset_colors(leds);

  /* uint8_t counter = 0; */
  /**/
  /* uint32_t colors[] = { */
  /*     urgb_u32(25, 0, 0),  // red */
  /*     urgb_u32(0, 25, 0),  // green */
  /*     urgb_u32(0, 0, 25),  // blue */
  /*     urgb_u32(25, 25, 0), // yellow */
  /*     urgb_u32(0, 25, 25), // cyan */
  /*     urgb_u32(25, 0, 25), // magenta */
  /*     urgb_u32(25, 12, 0), // orange */
  /*     urgb_u32(25, 25, 25) // white */
  /* }; */
  /**/
  /* uint32_t ledoff = 0; */
  /* uint32_t col = urgb_u32(5, 0, 5); */

  while (true) {
    qlock_leds_reset_colors(leds);

    /* pixel_render_spinning_clockwise(leds); */
    pixel_render_serial(leds);

    /* read_DS3231(); */
    qlock_read_ds3231(&out_qlock);
    qlock_print(&out_qlock);

    set_minute_pixels(&out_qlock, &pio_mins);
    qlock_leds_sweep_words(leds, &pio_words);

    sleep_ms(100);
  }
}
