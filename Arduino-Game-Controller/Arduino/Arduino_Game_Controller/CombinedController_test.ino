
#include <Keypad.h>

// Joystick 1
const int joy1X = A0;
const int joy1Y = A1;
const int joy1SW = 6;

// Joystick 2
const int joy2X = A2;
const int joy2Y = A3;
const int joy2SW = 7;

// Physical buttons
const int button1 = 2;
const int button2 = 3;
const int button3 = 4;
const int button4 = 5;

// Dialpad
const byte ROWS = 4;
const byte COLS = 4;

char keys[ROWS][COLS] = {
  {'D', 'C', 'B', 'A'},
  {'#', '9', '6', '3'},
  {'0', '8', '5', '2'},
  {'*', '7', '4', '1'}
};

byte rowPins[ROWS] = {8, 9, 10, 11};
byte colPins[COLS] = {12, 13, A4, A5};

Keypad dialpad = Keypad(
  makeKeymap(keys), rowPins, colPins, ROWS, COLS
);

void setup() {
  pinMode(joy1SW, INPUT_PULLUP);
  pinMode(joy2SW, INPUT_PULLUP);

  pinMode(button1, INPUT_PULLUP);
  pinMode(button2, INPUT_PULLUP);
  pinMode(button3, INPUT_PULLUP);
  pinMode(button4, INPUT_PULLUP);

  Serial.begin(115200);
}

void loop() {
  // Update keypad state machine
  dialpad.getKeys();

  // Controller readings
  Serial.print("J1_X:");
  Serial.print(analogRead(joy1X));

  Serial.print(",J1_Y:");
  Serial.print(analogRead(joy1Y));

  Serial.print(",J1_SW:");
  Serial.print(digitalRead(joy1SW) == LOW ? 1 : 0);

  Serial.print(",J2_X:");
  Serial.print(analogRead(joy2X));

  Serial.print(",J2_Y:");
  Serial.print(analogRead(joy2Y));

  Serial.print(",J2_SW:");
  Serial.print(digitalRead(joy2SW) == LOW ? 1 : 0);

  Serial.print(",B1:");
  Serial.print(digitalRead(button1));

  Serial.print(",B2:");
  Serial.print(digitalRead(button2));

  Serial.print(",B3:");
  Serial.print(digitalRead(button3));

  Serial.print(",B4:");
  Serial.print(digitalRead(button4));

  // Send keypad press and release events
  for (int i = 0; i < LIST_MAX; i++) {
    if (dialpad.key[i].stateChanged) {
      char key = dialpad.key[i].kchar;

      if (dialpad.key[i].kstate == PRESSED) {
        Serial.print(",DIALPAD_DOWN:");
        Serial.print(key);
      } else if (dialpad.key[i].kstate == RELEASED) {
        Serial.print(",DIALPAD_UP:");
        Serial.print(key);
      }
    }
  }

  Serial.println();
  delay(10);
}
