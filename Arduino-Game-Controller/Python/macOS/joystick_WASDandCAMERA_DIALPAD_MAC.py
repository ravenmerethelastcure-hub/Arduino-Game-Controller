
import time
import serial
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button
from serial.tools import list_ports

# ==================== SETTINGS ====================

BAUD_RATE = 115200

J1_CENTER_X = 516
J1_CENTER_Y = 524

# J2 readings at rest
J2_CENTER_X = 498
J2_CENTER_Y = 533

DEAD_ZONE = 100
CONNECTION_TIMEOUT = 0.5

CAMERA_SPEED = 900
CAMERA_HZ = 120
SMOOTHING = 0.18

BACKSPACE_INITIAL_DELAY = 0.35
BACKSPACE_REPEAT_INTERVAL = 0.07

# ==================================================

# macOS input controllers (requires Accessibility permission)
keyboard = KeyboardController()
mouse = MouseController()

KEY_MAP = {
    "space": Key.space,
    "enter": Key.enter,
    "backspace": Key.backspace,
    "esc": Key.esc,
}

def key_down(key):
    keyboard.press(KEY_MAP.get(key, key))

def key_up(key):
    keyboard.release(KEY_MAP.get(key, key))

def key_press(key):
    keyboard.press(KEY_MAP.get(key, key))
    keyboard.release(KEY_MAP.get(key, key))

def mouse_down(button):
    mouse.press(Button.left if button == "left" else Button.right)

def mouse_up(button):
    mouse.release(Button.left if button == "left" else Button.right)

def mouse_move_relative(dx, dy):
    # pynput uses absolute screen coordinates; emulate relative movement.
    x, y = mouse.position
    mouse.position = (x + dx, y + dy)


ser = None
latest_values = {}
last_valid_data = 0.0
last_mouse_update = 0.0

held_keys = set()
mouse_buttons = set()

button_was_pressed = {
    "B1": False,
    "B2": False,
    "B3": False,
    "B4": False,
}

button_started_at = {}
button_release_after = {}

right_click_mode = True
j2_button_was_pressed = False

dialpad_backspace_held = False
last_backspace_repeat = 0.0

camera_x = 0.0
camera_y = 0.0


# ==================================================
# AUTOMATIC ARDUINO DETECTION
# ==================================================

def find_arduino_port():
    ports = list(list_ports.comports())

    if not ports:
        print("No serial ports found.")
        print("Connect the Arduino and try again.")
        return None

    print("\nAvailable serial ports:")

    for port in ports:
        print(f"  {port.device}: {port.description}")

    keywords = (
        "arduino",
        "ch340",
        "wch",
        "usb serial",
        "usb-serial",
    )

    candidates = []

    for port in ports:
        description = (
            (port.description or "") + " " +
            (port.manufacturer or "")
        ).lower()

        if any(word in description for word in keywords):
            candidates.append(port)

    if len(candidates) == 1:
        return candidates[0].device

    if len(candidates) > 1:
        print("\nMultiple possible Arduino devices found.")
    else:
        print("\nArduino not identified by name.")

    available = {port.device for port in ports}

    while True:
        choice = input(
            "Enter the Arduino port (e.g. /dev/cu.usbmodem...), "
            "or Q to quit: "
        ).strip().upper()

        if choice == "Q":
            return None

        if choice in available:
            return choice

        print("That port is not in the available port list.")


# ==================================================
# KEY AND MOUSE HELPERS
# ==================================================

def update_keys(desired_keys):
    global held_keys

    for key in held_keys - desired_keys:
        key_up(key)

    for key in desired_keys - held_keys:
        key_down(key)

    held_keys = set(desired_keys)


def update_mouse_button(button, should_hold):
    if should_hold and button not in mouse_buttons:
        mouse_down(button)
        mouse_buttons.add(button)

    elif not should_hold and button in mouse_buttons:
        mouse_up(button)
        mouse_buttons.remove(button)


def release_all_inputs():
    global dialpad_backspace_held

    for key in list(held_keys):
        try:
            key_up(key)
        except Exception:
            pass

    held_keys.clear()

    if dialpad_backspace_held:
        try:
            key_up("backspace")
        except Exception:
            pass

        dialpad_backspace_held = False

    for button in list(mouse_buttons):
        try:
            mouse_up(button)
        except Exception:
            pass

    mouse_buttons.clear()


# ==================================================
# DIALPAD
# ==================================================

def handle_dialpad_event(event):
    global dialpad_backspace_held
    global last_backspace_repeat

    event = event.strip()

    if event.startswith("DIALPAD_DOWN:"):
        key = event.split(":", 1)[1].strip()

        # Numbers: one press per physical tap.
        if key in "0123456789" and len(key) == 1:
            key_press(key)

        # A = Enter.
        elif key == "A":
            key_press("enter")

        # B = Backspace, repeating while held.
        elif key == "B":
            if not dialpad_backspace_held:
                dialpad_backspace_held = True
                key_press("backspace")
                last_backspace_repeat = time.monotonic()

        # C = Escape.
        elif key == "C":
            key_press("esc")

        # D, # and * are reserved.

    elif event.startswith("DIALPAD_UP:"):
        key = event.split(":", 1)[1].strip()

        if key == "B":
            dialpad_backspace_held = False


def update_backspace_repeat():
    global last_backspace_repeat

    if not dialpad_backspace_held:
        return

    now = time.monotonic()

    if now - last_backspace_repeat >= BACKSPACE_INITIAL_DELAY:
        key_press("backspace")
        last_backspace_repeat = now - (
            BACKSPACE_INITIAL_DELAY - BACKSPACE_REPEAT_INTERVAL
        )


# ==================================================
# SERIAL PARSER
# ==================================================

def parse_serial_line(line):
    values = {}
    events = []

    for field in line.strip().split(","):
        if ":" not in field:
            continue

        name, value = field.split(":", 1)
        name = name.strip()
        value = value.strip()

        if name in ("DIALPAD_DOWN", "DIALPAD_UP"):
            events.append(f"{name}:{value}")
            continue

        try:
            values[name] = int(value)
        except ValueError:
            continue

    required = {
        "J1_X", "J1_Y", "J2_X", "J2_Y",
        "J2_SW", "B1", "B2", "B3", "B4",
    }

    if not required.issubset(values):
        return None, events

    return values, events


# ==================================================
# CONTROLLER PROCESSING
# ==================================================

def process_controller(values):
    global right_click_mode
    global j2_button_was_pressed
    global camera_x, camera_y
    global last_mouse_update

    now = time.monotonic()

    # J1: character movement.
    desired_keys = set()

    j1_x = values["J1_X"]
    j1_y = values["J1_Y"]

    if j1_x < J1_CENTER_X - DEAD_ZONE:
        desired_keys.add("w")
    elif j1_x > J1_CENTER_X + DEAD_ZONE:
        desired_keys.add("s")

    if j1_y > J1_CENTER_Y + DEAD_ZONE:
        desired_keys.add("a")
    elif j1_y < J1_CENTER_Y - DEAD_ZONE:
        desired_keys.add("d")

    # Physical buttons.
    if values["B1"] == 0:
        desired_keys.add("f")

    if values["B2"] == 0:
        desired_keys.add("e")

    if values["B4"] == 0:
        desired_keys.add("space")

    update_keys(desired_keys)

    # B3: left mouse, supporting short taps and holds.
    b3_pressed = values["B3"] == 0

    if b3_pressed and not button_was_pressed["B3"]:
        button_started_at["B3"] = now
        button_release_after.pop("B3", None)

    elif not b3_pressed and button_was_pressed["B3"]:
        started = button_started_at.get("B3", now)

        if now - started < 0.05:
            button_release_after["B3"] = started + 0.05
        else:
            button_release_after.pop("B3", None)

    button_was_pressed["B3"] = b3_pressed

    b3_should_hold = b3_pressed

    if not b3_pressed and "B3" in button_release_after:
        if now < button_release_after["B3"]:
            b3_should_hold = True
        else:
            button_release_after.pop("B3", None)

    update_mouse_button("left", b3_should_hold)

    # J2 click: toggle right-click mode.
    j2_pressed = values["J2_SW"] == 1

    if j2_pressed and not j2_button_was_pressed:
        right_click_mode = not right_click_mode

    j2_button_was_pressed = j2_pressed

    # --------------------------------------------------
    # J2 CAMERA AXIS FIX
    #
    # Your readings:
    # Up    = J2_X: 0,    J2_Y: 534
    # Down  = J2_X: 1023, J2_Y: 534
    # Left  = J2_X: 498,  J2_Y: 1023
    # Right = J2_X: 498,  J2_Y: 0
    #
    # Therefore:
    # J2_Y controls horizontal camera movement.
    # J2_X controls vertical camera movement.
    # --------------------------------------------------

    j2_x = values["J2_X"]
    j2_y = values["J2_Y"]

    target_x = 0.0
    target_y = 0.0

    # Physical right (J2_Y decreases) moves cursor right.
    if abs(j2_y - J2_CENTER_Y) > DEAD_ZONE:
        target_x = (J2_CENTER_Y - j2_y) / 512.0

    # Physical up (J2_X decreases) moves cursor up.
    if abs(j2_x - J2_CENTER_X) > DEAD_ZONE:
        target_y = (j2_x - J2_CENTER_X) / 512.0

    target_x = max(-1.0, min(1.0, target_x))
    target_y = max(-1.0, min(1.0, target_y))

    camera_x += (target_x - camera_x) * SMOOTHING
    camera_y += (target_y - camera_y) * SMOOTHING

    update_mouse_button(
        "right",
        right_click_mode and (
            target_x != 0.0 or target_y != 0.0
        )
    )

    # Mouse movement.
    if now - last_mouse_update >= 1.0 / CAMERA_HZ:
        dx = int(camera_x * CAMERA_SPEED / CAMERA_HZ)
        dy = int(camera_y * CAMERA_SPEED / CAMERA_HZ)

        if dx != 0 or dy != 0:
            mouse_move_relative(dx, dy)

        last_mouse_update = now


# ==================================================
# MAIN
# ==================================================

def main():
    global ser, latest_values, last_valid_data
    global camera_x, camera_y

    print("======================================")
    print("   ARDUINO GAME CONTROLLER (macOS)")
    print("======================================")

    selected_port = find_arduino_port()

    if selected_port is None:
        print("No Arduino port selected. Exiting.")
        return

    try:
        print(f"\nConnecting to {selected_port}...")

        ser = serial.Serial(
            selected_port,
            BAUD_RATE,
            timeout=0.02,
        )

        time.sleep(2)
        ser.reset_input_buffer()

        print("Controller connected!")
        print("If keyboard/mouse input does not work, allow IDLE/Python")
        print("under System Settings > Privacy & Security > Accessibility.")
        print("0-9 = numbers | A = Enter")
        print("B = Backspace (hold to repeat)")
        print("C = Escape | D, #, * = reserved")
        print("Press Ctrl+C to stop.\n")

        last_valid_data = time.monotonic()

        while True:
            if ser.in_waiting:
                line = ser.readline().decode(
                    "utf-8", errors="ignore"
                ).strip()

                if line:
                    values, events = parse_serial_line(line)

                    for event in events:
                        handle_dialpad_event(event)

                    if values is not None:
                        latest_values = values
                        last_valid_data = time.monotonic()
                        process_controller(latest_values)

            update_backspace_repeat()

            # Release held inputs if Arduino stops responding.
            if time.monotonic() - last_valid_data > CONNECTION_TIMEOUT:
                release_all_inputs()
                camera_x = 0.0
                camera_y = 0.0
                last_valid_data = time.monotonic()

            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\nStopping controller...")

    except serial.SerialException as error:
        print("Serial connection error:", error)
        print("Check the Arduino connection and selected port.")

    finally:
        release_all_inputs()

        if ser is not None and ser.is_open:
            ser.close()

        print("Controller stopped safely.")


if __name__ == "__main__":
    main()
