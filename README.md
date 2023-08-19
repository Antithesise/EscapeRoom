# RPi-based Escape Room
This a college project.

## Operation
Press `Ctrl+D` to reset, and `Ctrl+C` to exit.

## Parts List
- 2 x [5v Micro servo](https://www.jaycar.com.au/arduino-compatible-9g-micro-servo-motor/p/YM2758)
- 1 x [Adafruit 1x4 keypad](https://www.adafruit.com/product/1332)

## Pins
Configurable in `config.py`, here are the default values:

|             | |        HEADER | PIN | DIAGRAM         | |             |
|:------------|-|--------------:|:---:|:----------------|-|------------:|
|             | |         `3V3` |     | `5V`            | | general use |
|             | |     `2 (SDA)` |     | `5V`            | |             |
|             | |     `3 (SCL)` |     | `GND`           | |             |
|             | |  `4 (GPCLK0)` |     | `14 (TXD)`      | |             |
|             | |         `GND` |     | `15 (RXD)`      | |             |
| combo btn 0 | |          `17` |     | `18 (PCM_CLK)`  | |             |
| combo btn 1 | |          `27` |     | `GND`           | |             |
| combo btn 2 | |          `22` |     | `23`            | | servo 0     |
|             | |         `3V3` |     | `24`            | | servo 1     |
| combo btn 3 | |   `10 (MOSI)` |     | `GND`           | |             |
|             | |    `9 (MISO)` |     | `25`            | |             |
|             | |   `11 (SCLK)` |     | `8 (CE0)`       | |             |
|             | |         `GND` |     | `7 (CE1)`       | |             |
|             | |   `0 (ID_SD)` |     | `1 (ID_SC)`     | |             |
|             | |           `5` |     | `GND`           | |             |
|             | |           `6` |     | `12 (PWM0)`     | | pwm 0       |
| pwm 1       | |   `13 (PWM1)` |     | `GND`           | |             |
|             | | `19 (PCM_FS)` |     | `16`            | |             |
|             | |          `26` |     | `20 (PCM_DIN)`  | |             |
|             | |         `GND` |     | `20 (PCM_DOUT)` | |             |

![RPi Pinout Diagram](https://www.raspberrypi.com/documentation/computers/images/GPIO-Pinout-Diagram-2.png)

## Credits
- [metachris](https://github.com/metachris), author of the [RPIO](https://github.com/metachris/RPIO) library

---
© 2023 Antithesise