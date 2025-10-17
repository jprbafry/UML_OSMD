from ui import Panel
from mux_tx_rx import SerialManager
import threading
import time
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Control Panel Parameters")
    parser.add_argument("--width", type=int, default=800, help="Panel width in pixels")
    parser.add_argument("--height", type=int, default=400, help="Panel height in pixels")
    parser.add_argument("--simulate", "-s", action="store_true", help="Run in simulation (file-based) mode instead of real serial")
    parser.add_argument("--port", "-p",default="/dev/ttyACM0", help="Serial port to use when not simulating (e.g. /dev/ttyACM0)")
    parser.add_argument("--baud", "-b",type=int, default=115200, help="Baud rate for the serial connection")
    parser.add_argument("--debug", "-d", action="store_true", help="Debug mode?")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Create the control panel
    ctrl_panel = Panel(width=args.width, height=args.height, fps=60)

    # Create SerialManager (name='A')
    sm = SerialManager(simulate=args.simulate, name='A', port=args.port, baud=args.baud, debug=args.debug)

    # Callback for received messages from B
    def on_receive(msg):
        try:
            vals = [float(v) for v in msg.split(',')]
            if len(vals) != 4:
                print(f"[A RECEIVED INVALID] {msg}")
                return

            # Update current values of knobs and sliders
            ctrl_panel.knobs[0].update_current_value(vals[3])
            ctrl_panel.sliders[0].update_current_value(vals[0])
            ctrl_panel.knobs[1].update_current_value(vals[2])
            ctrl_panel.sliders[1].update_current_value(vals[1])

        except Exception as e:
            print(f"{msg}")

    sm.on_receive = on_receive
    sm.start()

    # Thread to send values periodically
    def send_panel_values():
        last_msg = None  # remember last message sent

        while ctrl_panel.running:
            try:
                # Read current desired values from the panel
                val4 = ctrl_panel.knobs[0].new_des_val      # Motor 4 (PCB layout): Light Source Azimuthal
                val1 = ctrl_panel.sliders[0].new_des_val    # Motor 1 (PCB layout): Light Source Polar
                val3 = ctrl_panel.knobs[1].new_des_val      # Motor 3 (PCB layout): Detector Azimuthal
                val2 = ctrl_panel.sliders[1].new_des_val    # Motor 2 (PCB layout): Detector Polar

                # Format message
                msg = f"{val1:.1f},{val2:.1f},{val3:.1f},{val4:.1f}"

                # Only send if different from last one
                if msg != last_msg:
                    sm.send(msg)
                    last_msg = msg

            except Exception as e:
                print(f"[SEND ERROR] {e}")

            time.sleep(0.1)  # check/send every 100 ms

    threading.Thread(target=send_panel_values, daemon=True).start()

    # Run the panel (blocking)
    ctrl_panel.run()
