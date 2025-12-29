#include "dnsserver.h"
#include "pico/cyw43_arch.h"
#include "pico/stdlib.h"
#include <cyw43_ll.h>
#include <hardware/gpio.h>
#include <lwip/def.h>
#include <stdio.h>

#include <lwip/pbuf.h>
#include <lwip/tcp.h>

#include "dhcpserver.h"

#define DEBUG_printf printf;

#define SSID "qlock-wifi"
#define WIFI_PW "qlock4you!"

#define PIN_GREEN 0
#define PIN_YELLOW 1
#define PIN_RED 2

#define TCP_PORT 80
#define POLL_TIME_S 5
#define HTTP_GET "GET"
#define HTTP_RESPONSE_HEADERS                                                  \
  "HTTP/1.1 %d OK\nContent-Length: %d\nContent-Type: text/html; "              \
  "charset=utf-8\nConnection: close\n\n"
#define LED_TEST_BODY                                                          \
  "<html><body><h1>Hello from Pico.</h1><p>Led is %s</p><p><a "                \
  "href=\"?led=%d\">Turn led %s</a></body></html>"
#define LED_PARAM "led=%d"
#define LED_TEST "/ledtest"
#define LED_GPIO 0
#define HTTP_RESPONSE_REDIRECT                                                 \
  "HTTP/1.1 302 Redirect\nLocation: http://%s" LED_TEST "\n\n"

typedef struct TCP_SERVER_T_ {
  struct tcp_pcb *server_pcb;
  bool complete;
  ip_addr_t gw;
} TCP_SERVER_T;

typedef struct TCP_CONNECT_STATE_T_ {
  struct tcp_pcb *pcb;
  int sent_len;
  char headers[128];
  char result[256];
  int header_len;
  int result_len;
  ip_addr_t *gw;
} TCP_CONNECT_STATE_T;

int main() {
  stdio_init_all();

  // set pins
  gpio_init(PIN_RED);
  gpio_init(PIN_YELLOW);
  gpio_init(PIN_GREEN);

  gpio_set_dir(PIN_RED, true);
  gpio_set_dir(PIN_YELLOW, true);
  gpio_set_dir(PIN_GREEN, true);

  TCP_SERVER_T *state = calloc(1, sizeof(TCP_SERVER_T));
  if (!state) {
    DEBUG_printf("failed to allocate state\n");
    gpio_put(PIN_RED, 1);
    return 1;
  }

  // Initialise the Wi-Fi chip
  if (cyw43_arch_init()) {
    printf("Wi-Fi init failed\n");
    gpio_put(PIN_RED, 1);
    return -1;
  }

  gpio_put(PIN_YELLOW, 1);

  // Enable wifi station
  cyw43_arch_enable_sta_mode();

  cyw43_arch_enable_ap_mode(SSID, WIFI_PW, CYW43_AUTH_WPA2_AES_PSK);
  sleep_ms(1000);
  gpio_put(PIN_YELLOW, 1);

  ip4_addr_t mask;
  state->gw.addr = PP_HTONL(CYW43_DEFAULT_IP_AP_ADDRESS);
  mask.addr = PP_HTONL(CYW43_DEFAULT_IP_MASK);

  // start dhcp server
  dhcp_server_t dhcp_server;
  dhcp_server_init(&dhcp_server, &state->gw, &mask);

  // start dns server
  dns_server_t dns_server;
  dns_server_init(&dns_server, &state->gw);

  if (!tcp_server_open(state, ap_name)) {
    DEBUG_printf("failed to open server\n");
    return 1;
  }

  while (true) {

    cyw43_arch_poll();
    gpio_put(PIN_GREEN, 1);
  }
}
