import json
import asyncio
import serial
import serial.tools.list_ports
from typing import Callable, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SerialData:
    timestamp: str
    uid: str
    gas: int
    count: int
    headway_ms: int
    flag: str
    received_at: datetime


class SerialHandler:
    def __init__(self, baud_rate: int = 115200):
        self.serial_port: Optional[serial.Serial] = None
        self.baud_rate = baud_rate
        self.port_name: Optional[str] = None
        self.is_connected = False
        self.callback: Optional[Callable] = None

    @staticmethod
    def list_available_ports():
        """List all available serial ports"""
        ports = []
        for port, desc, hwid in serial.tools.list_ports.comports():
            ports.append({
                "port": port,
                "description": desc,
                "hwid": hwid
            })
        return ports

    def connect(self, port: str, baud_rate: int = None) -> bool:
        """Connect to a serial port"""
        try:
            if baud_rate:
                self.baud_rate = baud_rate
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.baud_rate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.port_name = port
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """Disconnect from serial port"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.is_connected = False

    async def read_data(self, callback: Callable[[SerialData], None]):
        """Read data from serial port asynchronously"""
        self.callback = callback
        buffer = ""
        
        while self.is_connected:
            try:
                if self.serial_port and self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data
                    
                    # Look for complete JSON lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        
                        if line:
                            try:
                                parsed = json.loads(line)
                                # Handle typos in field names
                                count = parsed.get('count', parsed.get('counay_ms', 0))
                                if count == 0 and 'counay_ms' in parsed:
                                    count = 0  # If only typo field exists, default to 0
                                
                                serial_data = SerialData(
                                    timestamp=parsed.get('timestamp', ''),
                                    uid=parsed.get('uid', ''),
                                    gas=parsed.get('gas', 0),
                                    count=count,
                                    headway_ms=parsed.get('headway_ms', 0),
                                    flag=parsed.get('flag', ''),
                                    received_at=datetime.now()
                                )
                                if callback:
                                    callback(serial_data)
                            except json.JSONDecodeError:
                                print(f"Failed to parse JSON: {line}")
                
                await asyncio.sleep(0.01)  # Prevent busy waiting
            except Exception as e:
                print(f"Error reading from serial: {e}")
                await asyncio.sleep(0.1)

    def change_baud_rate(self, new_baud_rate: int) -> bool:
        """Change baud rate (requires reconnection)"""
        if self.is_connected:
            self.disconnect()
        
        self.baud_rate = new_baud_rate
        
        if self.port_name:
            return self.connect(self.port_name, new_baud_rate)
        return True

    def get_status(self):
        """Get current connection status"""
        return {
            "is_connected": self.is_connected,
            "port": self.port_name,
            "baud_rate": self.baud_rate
        }
