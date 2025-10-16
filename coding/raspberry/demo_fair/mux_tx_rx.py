import threading
import os
import time
import logging

try:
    import serial
except ImportError:
    serial = None


# Logging Setup
logger = logging.getLogger("SerialManager")
logger.setLevel(logging.DEBUG) # log everything
ch = logging.StreamHandler() # print to console
logger.addHandler(ch) # attach handler


# Simulated serial port using text files for inter-process comms
class FileBackedFakeSerial:

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

        # ensure files exist
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

# Class to handle Tx/Rx data over real or simulated serial
class SerialManager:

    def __init__(self, port="/dev/ttyACM0", baud=38400, simulate=True, name=None, debug=False):
        self.running = threading.Event()
        self.send_queue = []
        self.lock = threading.Lock()
        self.on_receive = None
        self.simulate = simulate

        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        if simulate or serial is None:
            if not name:
                raise ValueError("Need name='A' or 'B' when simulate=True")
            logger.info(f"Using simulated serial as {name}")
            self.ser = FileBackedFakeSerial(name)
        else:
            try:
                logger.info(f"Opening real serial port {port} @ {baud}")

                self.ser = serial.Serial(
                    port=port,
                    baudrate=baud,
                    timeout=1
                )
                logger.info("Serial port opened successfully.")
                time.sleep(2)  # wait for Arduino reset

            except Exception as e:
                logger.error(f"Could not open {port}: {e}")
                logger.warning("Falling back to simulation mode.")
                self.ser = FileBackedFakeSerial(name or 'A')
                self.simulate = True

        self.tx_thread = threading.Thread(target=self.tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self.rx_loop, daemon=True)

    # Transmission Thread (function)
    def tx_loop(self):
        while self.running.is_set():
            with self.lock:
                if self.send_queue:
                    msg = self.send_queue.pop(0)
                    try:
                        self.ser.write((msg + "\n").encode('ascii'))
                        logger.debug(f"TX: {msg}")
                    except Exception as e:
                        logger.error(f"TX error: {e}")
            time.sleep(0.05)
        logger.debug("TX thread stopped")

    # Reception Thread (function)
    def rx_loop(self):
        while self.running.is_set():
            try:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    if self.on_receive:
                        self.on_receive(line)
                        logger.debug(f"RX: {line}")
                    else:
                        logger.debug(f"RX: {line}")
            except Exception as e:
                logger.error(f"RX error: {e}")
            time.sleep(0.005)
        logger.debug("RX thread stopped")

    
    def start(self):
        self.running.set()
        self.tx_thread.start()
        self.rx_thread.start()
        logger.info("SerialManager started")

    def stop(self):
        self.running.clear()
        time.sleep(0.2)
        try:
            self.ser.close()
        except Exception:
            pass
        logger.info("SerialManager stopped")

    
    def send(self, msg):
        with self.lock:
            self.send_queue.append(msg)
