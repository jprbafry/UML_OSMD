import sys
import os
import time
import argparse

from mux_tx_rx import SerialManager


def parse_args():
    parser = argparse.ArgumentParser(description="Motor Mockup (B) Serial Script")
    parser.add_argument("--simulate", "-s", action="store_true", help="Run in simulation (file-based) mode instead of real serial")
    parser.add_argument("--port", "-p",default="/dev/ttyACM0", help="Serial port to use when not simulating (e.g. /dev/ttyACM0)")
    parser.add_argument("--baud", "-b",type=int, default=38400, help="Baud rate for the serial connection")
    parser.add_argument("--debug", "-d", action="store_true", help="Debug mode?")
    parser.add_argument("--name", "-n", choices=['A', 'B'], required=True, help="Name of this node (A or B) for simulation mode")
    return parser.parse_args()

def main():
    args = parse_args()

    sm = SerialManager(simulate=args.simulate, port=args.port, baud=args.baud, name=args.name)

    def on_receive(msg):
        print(f"[{args.name} RECEIVED] {msg}")

    sm.on_receive = on_receive
    sm.start()

    try:
        counter = 0
        while True:
            sm.send(f"Hello from {args.name} {counter}")
            counter += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"Ctrl+C pressed — stopping {args.name}")
        sm.stop()


if __name__ == "__main__":
    main()
