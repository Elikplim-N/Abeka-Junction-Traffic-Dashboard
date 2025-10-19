import serial
import json
import time
import argparse
from datetime import datetime, timedelta
import random


class TrafficSimulator:
    """Simulates traffic sensor data for demonstration"""
    
    def __init__(self, port, baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None
        self.vehicle_count = 0
        self.uid_list = ["5E51B05", "593515", "639CA18", "7A2B4C9", "8C3D5E1"]
        
    def connect(self):
        """Connect to serial port"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1
            )
            print(f"✓ Connected to {self.port} at {self.baud_rate} baud")
            return True
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port"""
        if self.serial:
            self.serial.close()
            print("Disconnected")
    
    def send_data(self, gas, count, headway_ms):
        """Send simulated data to serial port"""
        if not self.serial or not self.serial.is_open:
            return False
        
        uid = random.choice(self.uid_list)
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        data = {
            "timestamp": timestamp,
            "uid": uid,
            "gas": gas,
            "count": count,
            "headway_ms": headway_ms,
            "flag": ""
        }
        
        json_str = json.dumps(data) + "\n"
        self.serial.write(json_str.encode())
        return True
    
    def simulate_free_flow(self, duration=10):
        """
        Simulate FREE FLOW traffic
        - Low gas emissions
        - Vehicles spaced out (high headway)
        - Moderate count
        """
        print("\n🟢 Simulating FREE FLOW traffic...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            gas = random.randint(50, 150)  # Low emissions
            self.vehicle_count += 1
            headway_ms = random.randint(3500, 5000)  # High headway = spaced out
            
            self.send_data(gas, self.vehicle_count, headway_ms)
            print(f"  Gas: {gas} ppm | Count: {self.vehicle_count} | Headway: {headway_ms}ms")
            time.sleep(0.5)
    
    def simulate_light_traffic(self, duration=10):
        """
        Simulate LIGHT traffic
        - Low-moderate emissions
        - Vehicles somewhat spaced
        """
        print("\n🟡 Simulating LIGHT traffic...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            gas = random.randint(150, 250)
            self.vehicle_count += 1
            headway_ms = random.randint(2500, 3500)  # Medium headway
            
            self.send_data(gas, self.vehicle_count, headway_ms)
            print(f"  Gas: {gas} ppm | Count: {self.vehicle_count} | Headway: {headway_ms}ms")
            time.sleep(0.5)
    
    def simulate_moderate_congestion(self, duration=10):
        """
        Simulate MODERATE congestion
        - Moderate emissions
        - Vehicles getting closer
        """
        print("\n🟠 Simulating MODERATE congestion...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            gas = random.randint(250, 350)
            self.vehicle_count += 1
            headway_ms = random.randint(1500, 2500)  # Lower headway
            
            self.send_data(gas, self.vehicle_count, headway_ms)
            print(f"  Gas: {gas} ppm | Count: {self.vehicle_count} | Headway: {headway_ms}ms")
            time.sleep(0.5)
    
    def simulate_heavy_congestion(self, duration=10):
        """
        Simulate HEAVY congestion
        - High emissions
        - Vehicles very close
        """
        print("\n🔴 Simulating HEAVY congestion...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            gas = random.randint(350, 450)
            self.vehicle_count += 1
            headway_ms = random.randint(800, 1500)  # Very low headway
            
            self.send_data(gas, self.vehicle_count, headway_ms)
            print(f"  Gas: {gas} ppm | Count: {self.vehicle_count} | Headway: {headway_ms}ms")
            time.sleep(0.5)
    
    def simulate_severe_congestion(self, duration=10):
        """
        Simulate SEVERE congestion
        - Very high emissions
        - Vehicles bumper-to-bumper
        """
        print("\n🔴🔴 Simulating SEVERE congestion...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            gas = random.randint(450, 600)
            self.vehicle_count += 1
            headway_ms = random.randint(300, 800)  # Very close vehicles
            
            self.send_data(gas, self.vehicle_count, headway_ms)
            print(f"  Gas: {gas} ppm | Count: {self.vehicle_count} | Headway: {headway_ms}ms")
            time.sleep(0.5)
    
    def simulate_congestion_cycle(self):
        """
        Simulate a full congestion cycle:
        FREE_FLOW → LIGHT → MODERATE → HEAVY → SEVERE → HEAVY → MODERATE → LIGHT → FREE_FLOW
        """
        print("\n" + "="*60)
        print("ABEKA JUNCTION - TRAFFIC CONGESTION DEMONSTRATION")
        print("="*60)
        
        try:
            self.simulate_free_flow(8)
            self.simulate_light_traffic(8)
            self.simulate_moderate_congestion(8)
            self.simulate_heavy_congestion(8)
            self.simulate_severe_congestion(10)
            self.simulate_heavy_congestion(8)
            self.simulate_moderate_congestion(8)
            self.simulate_light_traffic(8)
            self.simulate_free_flow(8)
            
            print("\n" + "="*60)
            print("✓ Demonstration complete!")
            print("="*60)
        except KeyboardInterrupt:
            print("\n\nSimulation stopped by user")


def main():
    parser = argparse.ArgumentParser(description='Traffic data simulator for Abeka Junction')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port (default: /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--mode', choices=['cycle', 'free', 'light', 'moderate', 'heavy', 'severe'],
                       default='cycle', help='Simulation mode')
    parser.add_argument('--duration', type=int, default=10, help='Duration per scenario (seconds)')
    
    args = parser.parse_args()
    
    simulator = TrafficSimulator(args.port, args.baud)
    
    if not simulator.connect():
        return
    
    try:
        if args.mode == 'cycle':
            simulator.simulate_congestion_cycle()
        elif args.mode == 'free':
            simulator.simulate_free_flow(args.duration)
        elif args.mode == 'light':
            simulator.simulate_light_traffic(args.duration)
        elif args.mode == 'moderate':
            simulator.simulate_moderate_congestion(args.duration)
        elif args.mode == 'heavy':
            simulator.simulate_heavy_congestion(args.duration)
        elif args.mode == 'severe':
            simulator.simulate_severe_congestion(args.duration)
    finally:
        simulator.disconnect()


if __name__ == '__main__':
    main()
