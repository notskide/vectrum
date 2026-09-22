import numpy as np

def calculate_composite_risk(weather_score: float, news_score: float, econ_score: float) -> dict:
    weights = np.array([0.30, 0.40, 0.30])
    scores = np.array([weather_score, news_score, econ_score])
    risk_index = float(np.sum(scores * weights) * 100)
    variance = float(np.std(scores))
    confidence = float(max(50.0, 100.0 - (variance * 50.0)))
    return {
        "risk_index": round(risk_index, 1),
        "confidence": round(confidence, 1)
    }
