# RPi-based Escape Room
This a college project.

## Operation
Press `Ctrl+D` to reset, and `Ctrl+C` to exit.

## Parts List
- 1 x [Raspberry Pi 4B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
- 1 x 1x4 keypad, such as the [Adafruit 1332](https://www.adafruit.com/product/1332)
- 3 x Reed Switch OR Touch Sensor
- 2 x 5v micro servo
- 2 x Passive buzzer (piezo)
- 1 x NPN Transistor
- 2 x Switch
- 5 x LED (20mA)
- 1 x Diode
- Resistors to make up the following resistances:
  - 6kΩ
  - 1kΩ
  - 33Ω

## Circuit Diagram
![Circuit Diagram](circuit.png)
If reed switches are unavailable, a touch sensor could alternatively be used in conjunction with a small piece of conductive material:
![Touch Sensor Circuit Diagram](touch-circuit.png)
Note: Diagram may not fully reflect layout of final design. All pin numbers can be changed in `config.py` (see below).

## Pin Configuration
Configurable in `config.py`, here are the default values:

|             | |        HEADER | PIN | DIAGRAM         | |             |
|:------------|-|--------------:|:---:|:----------------|-|------------:|
| input power | |         `3V3` |     | `5V`            | | led power   |
|             | |     `2 (SDA)` |     | `5V`            | | servo power |
|             | |     `3 (SCL)` |     | `GND`           | | led gnd     |
|             | |  `4 (GPCLK0)` |     | `14 (TXD)`      | | led control |
|             | |         `GND` |     | `15 (RXD)`      | |             |
| combo btn 1 | |          `17` |     | `18 (PCM_CLK)`  | |             |
| combo btn 2 | |          `27` |     | `GND`           | | servo gnd   |
| combo btn 3 | |          `22` |     | `23`            | | servo 1     |
|             | |         `3V3` |     | `24`            | | servo 2     |
| combo btn 4 | |   `10 (MOSI)` |     | `GND`           | |             |
| disarm keys | |    `9 (MISO)` |     | `25`            | |             |
| ctrl rods   | |   `11 (SCLK)` |     | `8 (CE0)`       | |             |
|             | |         `GND` |     | `7 (CE1)`       | |             |
|             | |   `0 (ID_SD)` |     | `1 (ID_SC)`     | |             |
|             | |           `5` |     | `GND`           | |             |
|             | |           `6` |     | `12 (PWM0)`     | | buzzer 1    |
| buzzer 2    | |   `13 (PWM1)` |     | `GND`           | | buzzer gnd  |
|             | | `19 (PCM_FS)` |     | `16`            | |             |
|             | |          `26` |     | `20 (PCM_DIN)`  | |             |
|             | |         `GND` |     | `21 (PCM_DOUT)` | |             |

![RPi Pinout Diagram](https://www.raspberrypi.com/documentation/computers/images/GPIO-Pinout-Diagram-2.png)

## Credits
- [metachris](https://github.com/metachris), author of the [RPIO](https://github.com/metachris/RPIO) library
- [Circuit Diagram](https://www.circuit-diagram.org), for generation of circuit diagrams
- [StackOverflow](https://stackoverflow.com/) Users et al

---
© 2023 Antithesise