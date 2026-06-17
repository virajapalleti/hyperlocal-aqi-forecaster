# src/aqi_utils.py
# Maps a PM2.5 concentration to an AQI category + health guidance.

def pm25_to_category(pm25):
    """
    Return (category, color, health_message) for a PM2.5 value (µg/m³).
    Bands follow India's National AQI breakpoints for PM2.5 (24h).
    """
    if pm25 is None:
        return ("Unknown", "#888888", "No data available.")

    if pm25 <= 30:
        return ("Good", "#4caf50",
                "Air quality is good. Minimal impact.")
    elif pm25 <= 60:
        return ("Satisfactory", "#a3c853",
                "Minor breathing discomfort possible for sensitive people.")
    elif pm25 <= 90:
        return ("Moderate", "#ffeb3b",
                "Breathing discomfort for people with lung/heart conditions.")
    elif pm25 <= 120:
        return ("Poor", "#ff9800",
                "Breathing discomfort for most people on prolonged exposure.")
    elif pm25 <= 250:
        return ("Very Poor", "#f44336",
                "Respiratory illness on prolonged exposure. Limit outdoor activity.")
    else:
        return ("Severe", "#9c27b0",
                "Serious health impact for all. Avoid outdoor activity.")