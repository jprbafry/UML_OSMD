import threading
import time
import serial

# Configuration
PORT = 'COM5'   # Change to your COM port
BAUD = 9600
LOOPBACK = True  # If True, the sender's output will also go to receiver


try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    ser.flush()
    print(f"Serial port {PORT} opened at {BAUD} baud.", flush=True)
except serial.SerialException as e:
    print(f"Error opening serial port {PORT}: {e}")
    exit(1)


def sender():
    counter = 0
    while True:
        msg = f"Hello {counter}\n"
        ser.write(msg.encode('ascii'))
        print(f"[TX] {msg.strip()}", flush=True)
        counter += 1
        time.sleep(1)


def receiver():
    line = ""
    while True:
        line = ser.readline().decode('ascii', errors='ignore').strip()
        print(f"[RX] {line}", flush=True)
        time.sleep(0.5)

t1 = threading.Thread(target=sender, daemon=True)
t2 = threading.Thread(target=receiver, daemon=True)

t1.start()
t2.start()

# Keep main thread alive
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
    ser.close()
