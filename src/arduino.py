import threading
from typing import Callable

import serial
import serial.tools.list_ports


class ArduinoSerial:
    def __init__(self, baudrate=9600) -> None:
        self.baudrate = baudrate
        self.thread = None

        self.ser = self.connect()
        self.onMessage: Callable[[str], None] | None = None

    @property
    def port(self) -> str | None:
        return self.ser.port if self.ser else None


    def findArduinoPort(self) -> str | None:
        ports = serial.tools.list_ports.comports()

        for port in ports:
            return port.device

        return None

    def connect(self) -> serial.Serial | None:
        port = self.findArduinoPort()

        try: 
            return serial.Serial(port, self.baudrate, 1)
        except Exception:
            pass

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.readLoop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

        if self.ser:
            self.ser.close()

    def send(self, data: str) -> None:
        if self.ser and self.ser.is_open:
            self.ser.write((data + "\n").encode())

    def readLoop(self):
        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode(errors="ignore").strip()

                    if line:
                        if self.onMessage:
                            self.onMessage(line)

            except Exception:
                self.stop()

arduino = ArduinoSerial()
