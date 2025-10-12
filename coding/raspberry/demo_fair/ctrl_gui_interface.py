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
    parser.add_argument("--port", "-p",default="COM5", help="Serial port to use when not simulating (e.g. COM5)")
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
            ctrl_panel.knobs[0].update_current_value(vals[0])
            ctrl_panel.sliders[0].update_current_value(vals[1])
            ctrl_panel.knobs[1].update_current_value(vals[2])
            ctrl_panel.sliders[1].update_current_value(vals[3])

        except Exception as e:
            print(f"[A RECEIVE ERROR] {e}")

    sm.on_receive = on_receive
    sm.start()

    # Thread to send values periodically
    def send_panel_values():
        while ctrl_panel.running:
            try:
                # Read values from panel (knobs and sliders)
                val1 = ctrl_panel.knobs[0].new_des_val
                val2 = ctrl_panel.sliders[0].new_des_val
                val3 = ctrl_panel.knobs[1].new_des_val
                val4 = ctrl_panel.sliders[1].new_des_val

                msg = f"{val1:.1f},{val2:.1f},{val3:.1f},{val4:.1f}"
                sm.send(msg)
            except Exception as e:
                print(f"[SEND ERROR] {e}")
            time.sleep(0.1)  # send every 100ms

    threading.Thread(target=send_panel_values, daemon=True).start()

    # Run the panel (blocking)
    ctrl_panel.run()
