import threading
import time
import argparse
from mux_tx_rx import SerialManager


# Update desired values based on data received
def on_receive(msg, des_val, lock):
    try:
        vals = [float(v) for v in msg.split(',')]
        with lock:
            for i in range(4):
                des_val[i] = vals[i]
    except Exception as e:
        print(f"[B RECEIVE ERROR] {e}")


# Update current values (towards desired values)
def update_cur_val(cur_val, des_val, lock):
    micro_step_duration = 10 # [ms]
    while True:
        with lock:
            for i in range(4):
                if abs(cur_val[i] - des_val[i]) < 0.1:
                    cur_val[i] = des_val[i]
                elif cur_val[i] < des_val[i]:
                    cur_val[i] += 0.1
                elif cur_val[i] > des_val[i]:
                    cur_val[i] -= 0.1
        time.sleep(micro_step_duration/1000)


# Argument Parsing
def parse_args():
    parser = argparse.ArgumentParser(description="Motor Mockup (B) Serial Script")
    parser.add_argument("--simulate", "-s", action="store_true", help="Run in simulation (file-based) mode instead of real serial")
    parser.add_argument("--port", "-p",default="/dev/ttyACM0", help="Serial port to use when not simulating (e.g. /dev/ttyACM0)")
    parser.add_argument("--baud", "-b",type=int, default=38400, help="Baud rate for the serial connection")
    parser.add_argument("--debug", "-d", action="store_true", help="Debug mode?")
    return parser.parse_args()


# Main
def main():

    args = parse_args()

    # Initialize variables
    sm = SerialManager(simulate=args.simulate, name='B', port=args.port, baud=args.baud, debug=args.debug)
    cur_val = [0.0, 0.0, 0.0, 0.0] # Current Values (Motor Angular Positions)
    des_val = [0.0, 0.0, 0.0, 0.0] # Desired Values (Motor Angular Positions)
    lock = threading.Lock()

    # Assign on_receive callback
    sm.on_receive = lambda msg: on_receive(msg, des_val, lock)
    sm.start()

    # Start thread to update current values
    threading.Thread(target=update_cur_val, args=(cur_val, des_val, lock), daemon=True).start()

    # Send Motor Updates every 100ms
    update_period = 100 # [ms]
    try:
        while True:
            with lock:
                msg = ','.join(f"{v:.1f}" for v in cur_val)
            sm.send(msg)
            time.sleep(update_period/1000) 
    except KeyboardInterrupt:
        sm.stop()

if __name__ == "__main__":
    main()
