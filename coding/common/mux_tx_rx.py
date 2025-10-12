import threading
import os
import time

try:
    import serial
except ImportError:
    serial = None


class FileBackedFakeSerial:
    """Simulated serial port using text files for inter-process comms."""
    def __init__(self, name):
        self.name = name.upper()
        base = os.path.dirname(__file__)
        if self.name == 'A':
            self.write_file = os.path.join(base, 'a_to_b.txt')
            self.read_file  = os.path.join(base, 'b_to_a.txt')
        elif self.name == 'B':
            self.write_file = os.path.join(base, 'b_to_a.txt')
            self.read_file  = os.path.join(base, 'a_to_b.txt')
        else:
            raise ValueError("Name must be 'A' or 'B'")

        for f in [self.write_file, self.read_file]:
            open(f, 'a').close()

    def write(self, data: bytes):
        with open(self.write_file, 'a', encoding='utf-8') as f:
            f.write(data.decode('ascii'))

    def readline(self) -> bytes:
        line = ''
        with open(self.read_file, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                line = lines[0]
                f.seek(0)
                f.writelines(lines[1:])
                f.truncate()
        return line.encode('ascii')

    def flush(self):
        pass
    def close(self):
        pass


class SerialManager:
    """Handles sending and receiving data over real or simulated serial."""
    def __init__(self, port="COM5", baud=9600, simulate=True, name=None):
        self.running = threading.Event()
        self.send_queue = []
        self.lock = threading.Lock()
        self.on_receive = None
        self.simulate = simulate

        if simulate or serial is None:
            if not name:
                raise ValueError("Need name='A' or 'B' when simulate=True")
            print(f"[INFO] Using simulated serial as {name}")
            self.ser = FileBackedFakeSerial(name)
        else:
            try:
                print(f"[INFO] Opening real serial port {port} @ {baud}")
                self.ser = serial.Serial(
                    port=port,
                    baudrate=baud,
                    timeout=0.1, # don't block forever
                    write_timeout=0.1 # don't block forever
                )
                print("[INFO] Serial port opened successfully.")
            except Exception as e:
                print(f"[ERROR] Could not open {port}: {e}")
                print("[WARN] Falling back to simulation mode.")
                self.ser = FileBackedFakeSerial(name or 'A')
                self.simulate = True

        self.tx_thread = threading.Thread(target=self.tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self.rx_loop, daemon=True)

    def tx_loop(self):
        while self.running.is_set():
            with self.lock:
                if self.send_queue:
                    msg = self.send_queue.pop(0)
                    try:
                        self.ser.write((msg + "\n").encode('ascii'))
                        print(f"[TX] {msg}")
                    except Exception as e:
                        print(f"[TX-ERROR] {e}")
            time.sleep(0.05)
        print("[THREAD] TX stopped")

    def rx_loop(self):
        while self.running.is_set():
            try:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    if self.on_receive:
                        self.on_receive(line)
                    else:
                        print(f"[RX] {line}")
            except Exception as e:
                print(f"[RX-ERROR] {e}")
            time.sleep(0.05)
        print("[THREAD] RX stopped")

    def start(self):
        self.running.set()
        self.tx_thread.start()
        self.rx_thread.start()

    def stop(self):
        self.running.clear()
        time.sleep(0.2)
        try:
            self.ser.close()
        except Exception:
            pass
        print("[INFO] SerialManager stopped")

    def send(self, msg):
        with self.lock:
            self.send_queue.append(msg)
