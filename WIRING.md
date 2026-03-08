# RGB LED Wiring - Raspberry Pi

## LED pin identification

Hold the LED with the **flat side facing you**, pins pointing down.
Left to right:

```
 1    2    3    4
 R   ???   G    B
      ↑
  longest pin
```

This LED is **common cathode** - longest pin = GND.

## Resistor values

| Channel | Forward voltage | Resistor |
|---------|----------------|----------|
| Red     | ~2.0 V         | 150 Ω    |
| Green   | ~2.1 V         | 150 Ω    |
| Blue    | ~3.0 V         |  33 Ω    |

> If you only have one resistor value, **100 Ω for all three** is a safe substitute.

## Connections

| LED pin | Wire         | Pi header pin | BCM GPIO |
|---------|--------------|---------------|----------|
| 1 - R   | → 150 Ω → | Pin 11        | GPIO 17  |
| 2 - GND | → direct → | Pin 6         | GND      |
| 3 - G   | → 150 Ω → | Pin 13        | GPIO 27  |
| 4 - B   | →  33 Ω → | Pin 15        | GPIO 22  |

## Pi GPIO header (pins 1–15, odd row)

```
 3V3  [1] [2]  5V
GPIO2 [3] [4]  5V
GPIO3 [5] [6]  GND  ← GND (LED pin 2)
GPIO4 [7] [8]  GPIO14
 GND  [9] [10] GPIO15
GPIO17[11] [12] GPIO18  ← R  (LED pin 1, via 150 Ω)
GPIO27[13] [14] GND     ← G  (LED pin 3, via 150 Ω)
GPIO22[15] [16] GPIO23  ← B  (LED pin 4, via 33 Ω)
```

## Pin constants in `gpio_led.py`

```python
PIN_RED   = 17
PIN_GREEN = 27
PIN_BLUE  = 22
```

Change these if you use different GPIO pins.
