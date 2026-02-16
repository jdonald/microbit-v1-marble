# micro:bit V1 Marble Puzzle

A tilt-controlled puzzle game for the BBC micro:bit V1. Roll a marble across the 5x5 LED grid by tilting the board and guide it into a U-shaped receptacle. Each time you succeed, a new randomly generated level begins.

## How to Play

Hold the micro:bit flat and tilt it to roll the marble. The steeper the tilt, the faster the marble rolls. The marble moves freely in any direction (not just up/down/left/right) and bounces off the edges of the grid.

Your goal is to guide the marble into the receptacle — a pocket walled on three sides with one opening. You must approach from the open side to get the marble in.

### LED Legend

| Brightness | Element |
|------------|---------|
| Bright (9) | Marble — the ball you're rolling |
| Medium, blinking (5) | Target — the inside of the receptacle |
| Dim, steady (2) | Walls — the three sides of the receptacle |

When you get the marble into the target, a star flashes for one second and a new puzzle is generated.

## Requirements

- BBC micro:bit **V1** (also works on V2)
- USB cable (micro-USB)
- Python 3.6+

## Setup and Flashing

### 1. Install the flashing tool

```bash
pip install uflash
```

### 2. Connect the micro:bit

Plug the micro:bit into your computer via USB. It should appear as a USB drive named `MICROBIT`.

### 3. Flash the game

```bash
uflash main.py
```

This compiles the MicroPython script and flashes it to the connected micro:bit. The game starts automatically.

### Alternative: Manual copy

If `uflash` doesn't work for your setup, you can use any MicroPython tool that produces a `.hex` file, then drag and drop it onto the `MICROBIT` USB drive.

You can also paste `main.py` into the [micro:bit Python Editor](https://python.microbit.org/) and flash from the browser.

## Platform Notes

### Linux

You may need permission to access the USB device. If `uflash` fails with a permission error:

```bash
# Option 1: run with sudo
sudo uflash main.py

# Option 2: add a udev rule (persistent fix)
sudo tee /etc/udev/rules.d/50-microbit.rules << 'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="0d28", MODE="0664", GROUP="plugdev"
EOF
sudo udevadm control --reload-rules
# Then unplug and replug the micro:bit
```

### macOS

Works out of the box. The micro:bit mounts as `/Volumes/MICROBIT`.

### Windows

Works from Command Prompt or PowerShell. The micro:bit appears as a removable drive (e.g., `D:\`). Make sure Python is in your PATH.

## Project Structure

```
main.py       — the complete game (MicroPython)
README.md     — this file
LICENSE       — MIT license
```

## License

MIT
