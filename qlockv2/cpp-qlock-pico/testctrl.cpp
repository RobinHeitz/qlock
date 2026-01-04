#include "ledcontroller.hpp"
#include <chrono>
#include <cstdio>
#include <iostream>
#include <thread>

int main(int argc, char **argv) {
  // QlockConfig config = {.rot = Rotation::r90};
  // QlockConfig config = {.rot = Rotation::r180};
  QlockConfig config = {.rot = Rotation::r270};
  QlockController ctrl(config);

  std::chrono::milliseconds t(500);

  while (true) {
    ctrl.qlock();
    std::this_thread::sleep_for(t);
    std::printf(".\n");
  }
}
