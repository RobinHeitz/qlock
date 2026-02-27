#include <stdint.h>
#include <stdio.h>
#include <unistd.h>

#define GRID_SIZE 14
#define LED_COUNT GRID_SIZE *GRID_SIZE
#define MAX_WORD_LENGTH 10
#define WORD_COUNT 10

/*
1 2 3   10 11 12   19 20 21
6 5 4   15 14 13   24 23 22
7 8 9   16 17 18   25 26 27

*/

typedef struct {
  uint8_t ids[MAX_WORD_LENGTH];
  uint8_t length;
  char *rep;
} word;

typedef struct {
  word words[WORD_COUNT];
  char trep;
} qlock;

char tchars[LED_COUNT];

void init_terminal_chars(char *term_chars, uint8_t size) {
  for (int i = 0; i < LED_COUNT; i++) {
    term_chars[i] = ' ';
  }

  word w1 = {
      .length = 4,
      .ids = {1, 2, 3, 4},
      .rep = "ZEHN",
  };

  for (int i = 0; i < w1.length; i++) {
    char c = w1.rep[i];
    uint8_t index = w1.ids[i];
    tchars[index] = c;
  }
}

void clrscr() { printf("\e[1;1H\e[2J"); }

void print_qlock_terminal() {
  for (int i = 0; i < LED_COUNT; i++) {
    if (i > 10) {
      return;
    }
    printf("%d %c \n", i, tchars[i]);
  }
}

int main(int argc, char *argv[]) {
  if (argc > 1) {
    printf("Parameter: %c\n", *argv[1]);
  }

  printf("Hello there\n");

  init_terminal_chars(tchars, LED_COUNT);

  sleep(1);
  while (1) {
    printf("\033[2J\033[H");
    /* clrscr(); */
    print_qlock_terminal();
    sleep(10);

    // get qlock
    // compute pixels
    // iterate over all ids
  }
}
