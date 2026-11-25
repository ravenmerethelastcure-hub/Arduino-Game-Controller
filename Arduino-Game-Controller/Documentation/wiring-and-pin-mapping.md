\# Hardware Wiring and Pin Mapping



\## Components Used



\- Arduino Uno

\- 2 Analog Joystick Modules

\- 4 Push Buttons

\- 1 4×4 Matrix Keypad

\- Jumper Wires

\- USB Cable



\## Joystick Connections



| Joystick | Arduino Pin |

|---|---|

| Joystick 1 X-axis | A0 |

| Joystick 1 Y-axis | A1 |

| Joystick 1 Switch | D6 |

| Joystick 2 X-axis | A2 |

| Joystick 2 Y-axis | A3 |

| Joystick 2 Switch | D7 |



\## Push Button Connections



| Button | Arduino Pin |

|---|---|

| B1 | D2 |

| B2 | D3 |

| B3 | D4 |

| B4 | D5 |



\## Keypad Connections



| Keypad Pin | Arduino Pin |

|---|---|

| Row 1 | D8 |

| Row 2 | D9 |

| Row 3 | D10 |

| Row 4 | D11 |

| Column 1 | D12 |

| Column 2 | D13 |

| Column 3 | A4 |

| Column 4 | A5 |



\## Communication



The Arduino Uno communicates with the Python bridge through USB serial communication at 115200 baud.



The Python program reads the incoming data and translates it into keyboard and mouse inputs for the game.



\## Controller Mapping



\- Joystick 1: Player movement

\- Joystick 2: Camera movement

\- B1: F

\- B2: E

\- B3: Left mouse click

\- B4: Space

\- Keypad 0–9: Number input

\- Keypad A: Enter

\- Keypad B: Backspace

\- Keypad C: Escape



\*\*Note:\*\* All connections should be checked against the actual Arduino sketch and physical wiring before assembly.

