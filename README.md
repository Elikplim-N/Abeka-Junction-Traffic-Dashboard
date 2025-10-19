# Traffic Congestion Prediction Dashboard

A real-time dashboard for monitoring traffic congestion using serial sensor data. Visualize gas emissions (proxy for traffic), vehicle counts, and traffic patterns.

## Features

- 🔌 **Serial Port Connection**: Connect to your device via serial port with configurable baud rates (default 115200)
- 📊 **Real-time Visualization**: Live charts showing gas levels, vehicle counts, and headway times
- 📈 **Multiple Chart Types**: Area charts, bar charts, and line charts for different metrics
- 📱 **Responsive Design**: Works on desktop and tablet devices
- ⚡ **WebSocket Streaming**: Real-time data updates via WebSocket
- 🎯 **Statistics**: Live calculations of avg/min/max gas levels and total vehicle count

## Project Structure

```
traffic-dashboard/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── serial_handler.py    # Serial communication module
│   └── requirements.txt     # Python dependencies
└── frontend/
    ├── src/
    │   ├── Dashboard.jsx    # Main dashboard component
    │   ├── Dashboard.css    # Dashboard styles
    │   ├── App.jsx          # App entry point
    │   └── index.js         # React entry point
    ├── public/
    │   └── index.html       # HTML template
    └── package.json         # Node dependencies
```

## Installation

### Backend Setup

1. Navigate to backend directory:
```bash
cd traffic-dashboard/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd traffic-dashboard/frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at `http://localhost:8000`

### Start Frontend

In a new terminal:

```bash
cd frontend
npm start
```

Frontend runs at `http://localhost:3000`

## API Endpoints

### REST Endpoints

- `GET /api/ports` - List available serial ports
- `POST /api/connect?port={port}&baud_rate={rate}` - Connect to device
- `POST /api/disconnect` - Disconnect from device
- `POST /api/baud-rate?new_baud_rate={rate}` - Change baud rate
- `GET /api/status` - Get connection status
- `GET /api/data?limit=100` - Get historical data
- `GET /health` - Health check

### WebSocket Endpoint

- `ws://localhost:8000/ws` - Real-time data streaming

## Data Format

The dashboard expects JSON data in the following format:

```json
{
  "timestamp": "2025-08-08T16:55:59Z",
  "uid": "639CA18",
  "gas": 978,
  "count": 1,
  "headway_ms": 0,
  "flag": ""
}
```

**Fields:**
- `timestamp`: ISO 8601 timestamp of the reading
- `uid`: Unique identifier (e.g., sensor ID)
- `gas`: Gas sensor reading (ppm)
- `count`: Vehicle count
- `headway_ms`: Time between vehicles in milliseconds
- `flag`: Status flag (empty or error code)

## Usage

1. **Connect Device**: 
   - Select your serial port from the dropdown
   - Choose a baud rate (default 115200)
   - Click "Connect"

2. **View Real-time Data**:
   - Charts update automatically as data arrives
   - Statistics calculate in real-time
   - Last 100 data points displayed

3. **Change Settings**:
   - Baud rate can be changed while connected
   - Serial port requires disconnection to change

## Configuration

### Baud Rates

Quick-select buttons for common rates:
- 9600
- 19200
- 38400
- 57600
- 115200 (default)
- 230400
- 460800

Custom baud rates can be entered manually.

## Development

### Backend

The backend uses FastAPI for REST API and WebSocket support:

- `serial_handler.py`: Handles serial communication and JSON parsing
- `main.py`: FastAPI application with endpoints and WebSocket support

### Frontend

React-based dashboard with:

- Real-time WebSocket connection for data streaming
- Recharts for visualization
- Responsive CSS Grid layout
- Axios for REST API calls

## Troubleshooting

### Cannot Connect to Device
- Ensure device is connected via USB
- Check that the correct port is selected
- Verify baud rate matches device configuration
- Try with administrator/sudo privileges on Linux/Mac

### No Data Appearing
- Verify device is sending data
- Check that JSON format matches expected structure
- Ensure WebSocket connection is established
- Check browser console for errors

### Connection Drops
- Check USB cable connection
- Try a different USB port
- Restart the backend server
- Reconnect the device

## License

MIT License
