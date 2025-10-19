import React, { useState, useEffect, useRef } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area, BarChart, Bar
} from 'recharts';
import axios from 'axios';
import './Dashboard.css';

const API_BASE_URL = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/ws'

const Dashboard = () => {
  const [ports, setPorts] = useState([]);
  const [selectedPort, setSelectedPort] = useState('');
  const [baudRate, setBaudRate] = useState(115200);
  const [customBaudRate, setCustomBaudRate] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [data, setData] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [prediction, setPrediction] = useState(null);
  const wsRef = useRef(null);

  const commonBaudRates = [9600, 19200, 38400, 57600, 115200, 230400, 460800];

  // Fetch available ports on mount
  useEffect(() => {
    fetchPorts();
    const interval = setInterval(fetchPorts, 3000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket connection
  useEffect(() => {
    if (isConnected) {
      connectWebSocket();
    }
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [isConnected]);

  const fetchPorts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/ports`);
      setPorts(response.data.ports);
    } catch (err) {
      console.error('Failed to fetch ports:', err);
    }
  };

  const connectWebSocket = () => {
    wsRef.current = new WebSocket(WS_URL);
    
    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
    };

    wsRef.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === 'data') {
        setData((prevData) => {
          const newData = [...prevData, message.payload];
          // Keep last 100 data points
          return newData.slice(-100);
        });
        // Update prediction if available
        if (message.payload.prediction) {
          setPrediction(message.payload.prediction);
        }
      } else if (message.type === 'status') {
        setStatus(message.payload);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
    };
  };

  const handleConnect = async () => {
    setLoading(true);
    setError('');
    
    if (!selectedPort) {
      setError('Please select a port');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/connect`, null, {
        params: {
          port: selectedPort,
          baud_rate: baudRate
        }
      });
      
      setIsConnected(true);
      setStatus(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to connect');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    setLoading(true);
    setError('');
    
    try {
      await axios.post(`${API_BASE_URL}/disconnect`);
      setIsConnected(false);
      setData([]);
      setStatus(null);
    } catch (err) {
      setError('Failed to disconnect');
    } finally {
      setLoading(false);
    }
  };

  const handleBaudRateChange = async (newBaudRate) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/baud-rate`, null, {
        params: { new_baud_rate: newBaudRate }
      });
      
      setBaudRate(newBaudRate);
      setStatus((prev) => ({ ...prev, baud_rate: newBaudRate }));
    } catch (err) {
      setError('Failed to change baud rate');
    } finally {
      setLoading(false);
    }
  };

  const calculateStatistics = () => {
    if (data.length === 0) return { avgGas: 0, maxGas: 0, minGas: 0, totalCount: 0 };
    
    const gases = data.map((d) => d.gas);
    const counts = data.map((d) => d.count);
    
    return {
      avgGas: (gases.reduce((a, b) => a + b, 0) / gases.length).toFixed(2),
      maxGas: Math.max(...gases),
      minGas: Math.min(...gases),
      totalCount: counts.reduce((a, b) => a + b, 0),
      dataPoints: data.length
    };
  };

  const stats = calculateStatistics();

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>🚗 Abeka Junction - Traffic Congestion Prediction</h1>
        <p className="subtitle">Real-time RFID sensor monitoring and traffic analysis</p>
        <p className="location">📍 Abeka Junction Traffic Management System</p>
      </header>

      <div className="dashboard-layout">
        {/* Control Panel */}
        <div className="control-panel">
          <h2>Connection Settings</h2>
          
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label>Select Serial Port</label>
            <select 
              value={selectedPort} 
              onChange={(e) => setSelectedPort(e.target.value)}
              disabled={isConnected}
            >
              <option value="">-- Select a port --</option>
              {ports.map((port) => (
                <option key={port.port} value={port.port}>
                  {port.port} - {port.description}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Baud Rate</label>
            <div className="baud-rate-selector">
              <div className="quick-baud-rates">
                {commonBaudRates.map((rate) => (
                  <button
                    key={rate}
                    className={`baud-btn ${baudRate === rate ? 'active' : ''}`}
                    onClick={() => {
                      setBaudRate(rate);
                      setCustomBaudRate('');
                    }}
                    disabled={loading}
                  >
                    {rate}
                  </button>
                ))}
              </div>
              <input
                type="number"
                placeholder="Custom baud rate"
                value={customBaudRate}
                onChange={(e) => {
                  setCustomBaudRate(e.target.value);
                  if (e.target.value) {
                    setBaudRate(parseInt(e.target.value));
                  }
                }}
                disabled={loading}
              />
            </div>
          </div>

          <div className="button-group">
            {!isConnected ? (
              <button 
                className="btn btn-primary" 
                onClick={handleConnect}
                disabled={!selectedPort || loading}
              >
                {loading ? 'Connecting...' : 'Connect'}
              </button>
            ) : (
              <button 
                className="btn btn-danger" 
                onClick={handleDisconnect}
                disabled={loading}
              >
                {loading ? 'Disconnecting...' : 'Disconnect'}
              </button>
            )}
          </div>

          <div className="export-section">
            <h3>📊 Export Data</h3>
            <button 
              className="btn btn-export"
              onClick={() => window.open('http://localhost:8000/api/export/readings-csv', '_blank')}
            >
              📥 Readings CSV
            </button>
            <button 
              className="btn btn-export"
              onClick={() => window.open('http://localhost:8000/api/export/predictions-csv', '_blank')}
            >
              📥 Predictions CSV
            </button>
            <button 
              className="btn btn-export"
              onClick={() => window.open('http://localhost:8000/api/export/all-csv', '_blank')}
            >
              📥 All Data CSV
            </button>
          </div>

          {status && (
            <div className="status-info">
              <h3>Status</h3>
              <p><strong>Port:</strong> {status.port || 'N/A'}</p>
              <p><strong>Baud Rate:</strong> {status.baud_rate || 'N/A'}</p>
              <p><strong>Connected:</strong> {status.is_connected ? '✓ Yes' : '✗ No'}</p>
              <p><strong>Data Points:</strong> {status.data_points || 0}</p>
            </div>
          )}
        </div>

        {/* Charts and Stats */}
        <div className="charts-section">
          {/* Prediction Panel */}
          {prediction && (
            <div className="prediction-panel">
              <h3>🚦 Congestion Prediction</h3>
              <div className="prediction-content">
                <div className="congestion-meter">
                  <div className={`congestion-level level-${prediction.congestion_status.toLowerCase()}`}>
                    <p className="level-value">{prediction.congestion_level}%</p>
                    <p className="level-status">{prediction.congestion_status}</p>
                  </div>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill" 
                      style={{width: `${prediction.confidence}%`}}
                    ></div>
                    <p>Confidence: {prediction.confidence}%</p>
                  </div>
                </div>
                
                <div className="factors-breakdown">
                  <h4>Contributing Factors:</h4>
                  <div className="factors-grid">
                    <div className="factor">
                      <span>Gas Emissions</span>
                      <div className="factor-bar"><div className="factor-fill" style={{width: `${prediction.factors.gas}%`}}></div></div>
                      <span className="factor-value">{prediction.factors.gas}%</span>
                    </div>
                    <div className="factor">
                      <span>Vehicle Count</span>
                      <div className="factor-bar"><div className="factor-fill" style={{width: `${prediction.factors.vehicle_count}%`}}></div></div>
                      <span className="factor-value">{prediction.factors.vehicle_count}%</span>
                    </div>
                    <div className="factor">
                      <span>Headway Time</span>
                      <div className="factor-bar"><div className="factor-fill" style={{width: `${prediction.factors.headway_time}%`}}></div></div>
                      <span className="factor-value">{prediction.factors.headway_time}%</span>
                    </div>
                  </div>
                </div>
                
                <div className="next-prediction">
                  <p><strong>Next Minute:</strong> {prediction.next_minute_prediction}% ({prediction.next_minute_status})</p>
                </div>
                
                {prediction.recommendations && prediction.recommendations.length > 0 && (
                  <div className="recommendations">
                    <h4>📋 Recommendations:</h4>
                    <ul>
                      {prediction.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Statistics Cards */}
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Avg Gas Level</h3>
              <p className="stat-value">{stats.avgGas}</p>
              <p className="stat-unit">ppm</p>
            </div>
            <div className="stat-card">
              <h3>Max Gas Level</h3>
              <p className="stat-value">{stats.maxGas}</p>
              <p className="stat-unit">ppm</p>
            </div>
            <div className="stat-card">
              <h3>Min Gas Level</h3>
              <p className="stat-value">{stats.minGas}</p>
              <p className="stat-unit">ppm</p>
            </div>
            <div className="stat-card">
              <h3>Total Count</h3>
              <p className="stat-value">{stats.totalCount}</p>
              <p className="stat-unit">vehicles</p>
            </div>
          </div>

          {/* Gas Level Chart */}
          <div className="chart-container">
            <h3>Gas Levels Over Time</h3>
            {data.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="colorGas" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  />
                  <YAxis />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#f5f5f5' }}
                    formatter={(value) => value.toFixed(2)}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="gas" 
                    stroke="#8884d8" 
                    fillOpacity={1}
                    fill="url(#colorGas)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <p className="no-data">No data yet. Connect to a device to start.</p>
            )}
          </div>

          {/* Vehicle Count Chart */}
          <div className="chart-container">
            <h3>Vehicle Count Distribution</h3>
            {data.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  />
                  <YAxis />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#f5f5f5' }}
                  />
                  <Bar dataKey="count" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="no-data">No data yet. Connect to a device to start.</p>
            )}
          </div>

          {/* Headway Time Chart */}
          <div className="chart-container">
            <h3>Vehicle Headway (Time Between Vehicles)</h3>
            {data.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  />
                  <YAxis label={{ value: 'Headway (ms)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#f5f5f5' }}
                    formatter={(value) => `${value} ms`}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="headway_ms" 
                    stroke="#ff7300"
                    dot={false}
                    name="Headway (ms)"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="no-data">No data yet. Connect to a device to start.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
