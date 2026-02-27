# Instructions

## Debugging

Compile with flag

`pico_enable_stdio_usb(cqlock 1)`
such that it outputs stdio over USB
`picocom -b 115200 /dev/tty.usbmodem112101`

press bootsel btn, then plug-in usb
`cp ./build/cqlock.uf2 /Volumes/RP2350`
