from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import asyncio
import json
import csv
import io
from collections import deque
from datetime import datetime
from serial_handler import SerialHandler, SerialData
from prediction_model import TrafficCongestionPredictor
from database import db
from typing import Set

app = FastAPI(title="Traffic Dashboard API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Global state
serial_handler = SerialHandler()
active_connections: Set[WebSocket] = set()
data_buffer = deque(maxlen=1000)  # Store last 1000 readings
read_task = None
predictor = TrafficCongestionPredictor(window_size=30)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting: {e}")


manager = ConnectionManager()


def data_callback(serial_data: SerialData):
    """Callback when data is received from serial"""
    # Add to predictor
    predictor.add_reading(
        gas=serial_data.gas,
        count=serial_data.count,
        headway_ms=serial_data.headway_ms,
        timestamp=serial_data.timestamp
    )
    
    # Get predictions
    congestion_pred = predictor.predict_congestion()
    next_pred = predictor.predict_next_minute()
    recommendations = predictor.get_recommendations()
    
    data_dict = {
        "timestamp": serial_data.timestamp,
        "uid": serial_data.uid,
        "gas": serial_data.gas,
        "count": serial_data.count,
        "headway_ms": serial_data.headway_ms,
        "flag": serial_data.flag,
        "received_at": serial_data.received_at.isoformat(),
        "prediction": {
            "congestion_level": congestion_pred["level"],
            "congestion_status": congestion_pred["status"],
            "confidence": congestion_pred["confidence"],
            "factors": congestion_pred["factors"],
            "next_minute_prediction": next_pred["prediction"],
            "next_minute_status": next_pred["status"],
            "recommendations": recommendations
        }
    }
    data_buffer.append(data_dict)
    
    # Save to database
    try:
        reading_id = db.insert_reading(
            timestamp=serial_data.timestamp,
            uid=serial_data.uid,
            gas=serial_data.gas,
            count=serial_data.count,
            headway_ms=serial_data.headway_ms,
            flag=serial_data.flag,
            received_at=serial_data.received_at.isoformat()
        )
        
        db.insert_prediction(
            sensor_reading_id=reading_id,
            congestion_level=congestion_pred["level"],
            congestion_status=congestion_pred["status"],
            confidence=congestion_pred["confidence"],
            next_minute_prediction=next_pred["prediction"],
            next_minute_status=next_pred["status"]
        )
    except Exception as e:
        print(f"Error saving to database: {e}")
    
    # Broadcast to all connected WebSocket clients
    asyncio.create_task(manager.broadcast({
        "type": "data",
        "payload": data_dict
    }))


@app.get("/api/ports")
async def get_available_ports():
    """Get list of available serial ports"""
    ports = SerialHandler.list_available_ports()
    return {"ports": ports}


@app.post("/api/connect")
async def connect_to_device(port: str, baud_rate: int = 115200):
    """Connect to a serial device"""
    global read_task
    
    if serial_handler.is_connected:
        serial_handler.disconnect()
    
    success = serial_handler.connect(port, baud_rate)
    
    if success:
        # Start reading task
        if read_task:
            read_task.cancel()
        read_task = asyncio.create_task(
            serial_handler.read_data(data_callback)
        )
        return {
            "status": "connected",
            "port": port,
            "baud_rate": baud_rate
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to connect")


@app.post("/api/disconnect")
async def disconnect_device():
    """Disconnect from serial device"""
    global read_task
    
    if read_task:
        read_task.cancel()
    
    serial_handler.disconnect()
    return {"status": "disconnected"}


@app.post("/api/baud-rate")
async def change_baud_rate(new_baud_rate: int):
    """Change baud rate (reconnects if connected)"""
    global read_task
    
    if serial_handler.is_connected:
        if read_task:
            read_task.cancel()
        
        success = serial_handler.change_baud_rate(new_baud_rate)
        
        if success:
            read_task = asyncio.create_task(
                serial_handler.read_data(data_callback)
            )
            return {
                "status": "success",
                "baud_rate": new_baud_rate
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to change baud rate")
    else:
        serial_handler.baud_rate = new_baud_rate
        return {
            "status": "success",
            "baud_rate": new_baud_rate
        }


@app.get("/api/status")
async def get_status():
    """Get current connection status"""
    return {
        **serial_handler.get_status(),
        "data_points": len(data_buffer)
    }


@app.get("/api/data")
async def get_historical_data(limit: int = 100):
    """Get historical data points"""
    data = list(data_buffer)[-limit:]
    return {"data": data}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data streaming"""
    await manager.connect(websocket)
    
    # Send current status
    await websocket.send_json({
        "type": "status",
        "payload": {
            **serial_handler.get_status(),
            "data_points": len(data_buffer)
        }
    })
    
    # Send recent data
    recent_data = list(data_buffer)[-50:]
    for data_point in recent_data:
        await websocket.send_json({
            "type": "data",
            "payload": data_point
        })
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except Exception as e:
        manager.disconnect(websocket)


@app.get("/api/prediction")
async def get_prediction():
    """Get current congestion prediction"""
    return predictor.predict_congestion()


@app.get("/api/prediction/next-minute")
async def get_next_minute_prediction():
    """Get next minute prediction"""
    return predictor.predict_next_minute()


@app.get("/api/recommendations")
async def get_recommendations():
    """Get traffic recommendations"""
    return {"recommendations": predictor.get_recommendations()}


@app.get("/api/db/readings")
async def get_db_readings(limit: int = 100, offset: int = 0):
    """Get sensor readings from database"""
    readings = db.get_readings(limit, offset)
    return {"readings": readings, "total": db.get_total_count()}


@app.get("/api/db/readings/{date}")
async def get_readings_by_date(date: str):
    """Get readings for specific date (YYYY-MM-DD)"""
    readings = db.get_readings_by_date(date)
    return {"date": date, "readings": readings, "count": len(readings)}


@app.get("/api/db/predictions")
async def get_db_predictions(limit: int = 100, offset: int = 0):
    """Get predictions from database"""
    predictions = db.get_predictions(limit, offset)
    return {"predictions": predictions}


@app.get("/api/db/statistics")
async def get_db_statistics(date: str = None):
    """Get daily statistics"""
    stats = db.get_statistics(date)
    return {"statistics": stats}


@app.get("/api/db/congestion-summary")
async def get_congestion_summary(hours: int = 24):
    """Get congestion summary for last N hours"""
    summary = db.get_congestion_summary(hours)
    return {"hours": hours, "summary": summary}


@app.get("/api/export/readings-csv")
async def export_readings_csv():
    """Export sensor readings as CSV"""
    readings = db.get_readings(limit=10000)
    
    output = io.StringIO()
    if readings:
        writer = csv.DictWriter(output, fieldnames=readings[0].keys())
        writer.writeheader()
        writer.writerows(readings)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=traffic_readings.csv"}
    )


@app.get("/api/export/predictions-csv")
async def export_predictions_csv():
    """Export predictions as CSV"""
    predictions = db.get_predictions(limit=10000)
    
    output = io.StringIO()
    if predictions:
        writer = csv.DictWriter(output, fieldnames=predictions[0].keys())
        writer.writeheader()
        writer.writerows(predictions)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=traffic_predictions.csv"}
    )


@app.get("/api/export/all-csv")
async def export_all_csv():
    """Export all data as CSV"""
    readings = db.get_readings(limit=10000)
    predictions = db.get_predictions(limit=10000)
    
    output = io.StringIO()
    
    # Export readings
    output.write("=== SENSOR READINGS ===\n")
    if readings:
        writer = csv.DictWriter(output, fieldnames=readings[0].keys())
        writer.writeheader()
        writer.writerows(readings)
    
    output.write("\n\n=== PREDICTIONS ===\n")
    if predictions:
        writer = csv.DictWriter(output, fieldnames=predictions[0].keys())
        writer.writeheader()
        writer.writerows(predictions)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=traffic_data_all.csv"}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
