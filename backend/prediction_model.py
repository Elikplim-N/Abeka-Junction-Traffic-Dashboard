import numpy as np
from collections import deque
from datetime import datetime, timedelta


class TrafficCongestionPredictor:
    """
    Traffic congestion prediction model based on:
    - Gas emissions (proxy for vehicle exhaust)
    - Vehicle count
    - Headway time (time between vehicles)
    - Historical trend analysis
    """
    
    def __init__(self, window_size=30):
        self.window_size = window_size
        self.gas_history = deque(maxlen=window_size)
        self.count_history = deque(maxlen=window_size)
        self.headway_history = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
    
    def add_reading(self, gas: int, count: int, headway_ms: int, timestamp: str):
        """Add a new reading to the model"""
        self.gas_history.append(gas)
        self.count_history.append(count)
        self.headway_history.append(headway_ms)
        self.timestamps.append(datetime.fromisoformat(timestamp.replace('Z', '+00:00')))
    
    def _normalize(self, value, min_val, max_val):
        """Normalize value to 0-1 range"""
        if max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)
    
    def _calculate_trend(self, history):
        """Calculate trend of a metric (increasing/decreasing)"""
        if len(history) < 2:
            return 0
        history_list = list(history)
        # Simple linear trend
        if len(history_list) >= 3:
            recent = np.array(history_list[-3:])
            trend = np.polyfit(range(len(recent)), recent, 1)[0]
            return trend
        return 0
    
    def predict_congestion(self):
        """
        Predict traffic congestion level (0-100)
        0 = Free flow, 50 = Moderate, 100 = Severe congestion
        """
        if len(self.gas_history) < 3:
            return {"level": 0, "status": "INSUFFICIENT_DATA", "confidence": 0}
        
        # Get current metrics
        current_gas = self.gas_history[-1]
        current_count = self.count_history[-1]
        current_headway = self.headway_history[-1]
        
        # Calculate averages
        avg_gas = np.mean(list(self.gas_history))
        avg_count = np.mean(list(self.count_history))
        avg_headway = np.mean(list(self.headway_history))
        
        # Normalize metrics (0-1)
        # Gas level: 0-2000 ppm (higher = more congestion)
        gas_factor = self._normalize(current_gas, 0, 2000)
        
        # Vehicle count: 0-10 per sample (higher = more congestion)
        count_factor = self._normalize(current_count, 0, 10)
        
        # Headway time: lower = more congestion (vehicles closer together)
        # Normal: 2000-5000ms, Congested: <1000ms
        headway_factor = 1 - self._normalize(current_headway, 0, 5000)
        headway_factor = max(0, min(1, headway_factor))
        
        # Calculate trends (positive = worsening)
        gas_trend = self._calculate_trend(self.gas_history)
        count_trend = self._calculate_trend(self.count_history)
        headway_trend = self._calculate_trend(self.headway_history)  # Negative = congestion worsening
        
        # Normalize trends
        trend_factor = max(0, min(1, (gas_trend + count_trend - headway_trend) / 10))
        
        # Weighted congestion score - headway is dominant
        weights = {
            'headway': 0.60,  # Dominant factor
            'gas': 0.20,
            'count': 0.15,
            'trend': 0.05
        }
        
        congestion_score = (
            headway_factor * weights['headway'] +
            gas_factor * weights['gas'] +
            count_factor * weights['count'] +
            trend_factor * weights['trend']
        )
        
        # Convert to 0-100 scale
        congestion_level = int(congestion_score * 100)
        
        # Determine status
        if congestion_level < 20:
            status = "FREE_FLOW"
        elif congestion_level < 40:
            status = "LIGHT"
        elif congestion_level < 60:
            status = "MODERATE"
        elif congestion_level < 80:
            status = "HEAVY"
        else:
            status = "SEVERE"
        
        # Calculate confidence (based on data points)
        confidence = min(100, len(self.gas_history) / self.window_size * 100)
        
        return {
            "level": congestion_level,
            "status": status,
            "confidence": int(confidence),
            "factors": {
                "gas": int(gas_factor * 100),
                "vehicle_count": int(count_factor * 100),
                "headway_time": int(headway_factor * 100),
                "trend": int(trend_factor * 100)
            },
            "metrics": {
                "current_gas": current_gas,
                "avg_gas": round(avg_gas, 2),
                "current_count": current_count,
                "avg_count": round(avg_count, 2),
                "current_headway": current_headway,
                "avg_headway": round(avg_headway, 2)
            }
        }
    
    def predict_next_minute(self):
        """Predict congestion for the next minute"""
        if len(self.gas_history) < 5:
            return {"prediction": 0, "status": "INSUFFICIENT_DATA"}
        
        # Simple linear extrapolation
        gas_trend = self._calculate_trend(self.gas_history)
        count_trend = self._calculate_trend(self.count_history)
        headway_trend = self._calculate_trend(self.headway_history)
        
        # Project forward
        predicted_gas = list(self.gas_history)[-1] + (gas_trend * 5)  # 5 samples ahead
        predicted_count = list(self.count_history)[-1] + (count_trend * 5)
        predicted_headway = list(self.headway_history)[-1] + (headway_trend * 5)
        
        # Ensure values stay in bounds
        predicted_gas = max(0, min(2000, predicted_gas))
        predicted_count = max(0, min(15, predicted_count))
        predicted_headway = max(0, predicted_headway)
        
        # Calculate predicted congestion with headway as dominant
        gas_factor = self._normalize(predicted_gas, 0, 2000)
        count_factor = self._normalize(predicted_count, 0, 10)
        headway_factor = 1 - self._normalize(predicted_headway, 0, 5000)
        headway_factor = max(0, min(1, headway_factor))
        
        predicted_level = int((headway_factor * 0.60 + gas_factor * 0.20 + count_factor * 0.15) * 100)
        
        if predicted_level < 20:
            status = "FREE_FLOW"
        elif predicted_level < 40:
            status = "LIGHT"
        elif predicted_level < 60:
            status = "MODERATE"
        elif predicted_level < 80:
            status = "HEAVY"
        else:
            status = "SEVERE"
        
        return {
            "prediction": predicted_level,
            "status": status,
            "change": predicted_level - int(self.predict_congestion()["level"])
        }
    
    def get_recommendations(self):
        """Get traffic management recommendations"""
        current = self.predict_congestion()
        next_min = self.predict_next_minute()
        level = current["level"]
        
        recommendations = []
        
        if level < 20:
            recommendations.append("Traffic is flowing freely. No action needed.")
        elif level < 40:
            recommendations.append("Light traffic detected. Routes are clear.")
        elif level < 60:
            recommendations.append("Moderate congestion. Consider alternative routes.")
            recommendations.append("Traffic signals may need adjustment for better flow.")
        elif level < 80:
            recommendations.append("Heavy congestion detected!")
            recommendations.append("Increase traffic signal cycle time on main roads.")
            recommendations.append("Consider activating alternate routes or public transport incentives.")
        else:
            recommendations.append("SEVERE congestion! Immediate action required.")
            recommendations.append("Activate emergency traffic management protocols.")
            recommendations.append("Redirect traffic via alternate routes.")
            recommendations.append("Increase public transport capacity.")
        
        if next_min["change"] > 10:
            recommendations.append("⚠️ Traffic is getting worse - condition worsening in next minute")
        elif next_min["change"] < -10:
            recommendations.append("✓ Traffic improving - condition should ease in next minute")
        
        return recommendations
