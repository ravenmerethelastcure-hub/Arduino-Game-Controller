# \# Arduino Game Controller

# 

# A custom Arduino-based game controller developed for \*\*Ravenmere: The Last Cure\*\*, a zombie-apocalypse escape game built in Roblox.

# 

# The controller uses an Arduino Uno, two analog joysticks, four push buttons and a 4×4 keypad to provide physical controls for gameplay.

# 

# \## Features

# 

# \- Dual joystick support for player movement and camera control.

# \- Four physical buttons for in-game actions.

# \- 4×4 keypad for entering puzzle codes.

# \- USB serial communication between Arduino and computer.

# \- Python bridge to translate hardware inputs into keyboard and mouse actions.

# \- Separate Windows and macOS Python implementations.

# 

# \## Hardware Requirements

# 

# \- Arduino Uno

# \- 2 × Analog joystick modules

# \- 4 × Push buttons

# \- 1 × 4×4 matrix keypad

# \- Jumper wires

# \- USB cable

# 

# \## Software Requirements

# 

# \### Arduino

# \- Arduino IDE

# \- Arduino Uno board support

# \- Any libraries required by the Arduino sketch

# 

# \### Windows

# 

# Install Python 3 and the required libraries:

# 

# ```bash

# py -m pip install pyserial pydirectinput

# ```

# 

# Run the Windows controller:

# 

# ```bash

# py joystick\_WASDandCAMERA\_DIALPAD.py

# ```

# 

# \### macOS

# 

# Install Python 3 and the required libraries:

# 

# ```bash

# python3 -m pip install pyserial pynput

# ```

# 

# Run the macOS controller:

# 

# ```bash

# python3 joystick\_WASDandCAMERA\_DIALPAD\_MAC.py

# ```

# 

# macOS may require Accessibility and Input Monitoring permissions for keyboard and mouse control.

# 

# \## Controller Mapping

# 

# | Hardware | Game Input |

# |---|---|

# | Joystick 1 | WASD movement |

# | Joystick 2 | Camera movement |

# | Joystick 2 switch | Toggle camera mode |

# | Button 1 | F |

# | Button 2 | E |

# | Button 3 | Left mouse click |

# | Button 4 | Space |

# | Keypad 0–9 | Number input |

# | Keypad A | Enter |

# | Keypad B | Backspace |

# | Keypad C | Escape |

# 

# \## Communication

# 

# The Arduino communicates with the Python bridge through USB serial communication at \*\*115200 baud\*\*.

# 

# The Python program receives the controller data and translates it into keyboard and mouse actions recognised by the game.

# 

# \## Repository Structure

# 

# \- `Arduino/` contains the Arduino sketch.

# \- `Python/Windows/` contains the Windows Python bridge.

# \- `Python/macOS/` contains the macOS Python bridge.

# \- `Documentation/` contains hardware wiring and pin mapping information.

# 

# \## Project Information

# 

# \*\*Game:\*\* Ravenmere: The Last Cure

# 

# \*\*Hardware:\*\* Arduino Uno

# 

# \*\*Communication:\*\* USB Serial

# 

# \*\*Baud Rate:\*\* 115200

