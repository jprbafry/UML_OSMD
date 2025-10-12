## Scripts Overview

**ui.py**  
- Contains the GUI components (knobs, sliders, labels) used by `ctrl_gui_interface.py`.  
- Handles drawing, updating, and reading values from the control panel interface.

**mux_tx_rx.py**  
- Provides a **SerialManager** class that handles sending and receiving data.  
- Can use real serial ports or simulate serial communication via files (`a_to_b.txt` and `b_to_a.txt`).  
- Supports assigning callback functions for received data.

**talker_mockup.py**  
- Demonstrates how `mux_tx_rx` works in **simulation mode**.  
- **Two instances** of the script should be run simultaneously to show how data are sent/received between two processes.

**motor_mockup.py**  
- Emulates a physical 4-motor system.  
- **Behavior:**
  - Receives desired motor positions.
  - Moves “current” motor positions gradually toward the desired positions.
  - Periodically reports current positions over serial.

**ctrl_cli_interface.py**  
- Provides a command-line interface for sending motor commands.  
- User inputs desired positions via terminal.  
- Communicates with `motor_mockup.py` through `mux_tx_rx`.

**ctrl_gui_interface.py**  
- Provides a graphical user interface (knobs and sliders) for sending motor commands.  
- Uses `ui.py` for rendering and interacting with the control panel.  
- Communicates with `motor_mockup.py` via `mux_tx_rx`.


## How to Run

```
python talker_mockup.py -s -n <A|B>
python motor_mockup.py -s
python ctrl_cli_interface.py -s
python ctrl_gui_interface.py -s
```
