# Hyperlocal AQI Forecaster — Delhi

24-hour PM2.5 forecasts for three Delhi air-quality monitoring stations, served from a live web dashboard.

**Live app:** https://hyperlocal-aqi-forecaster.onrender.com/

> Hosted on Render's free tier. First visit after inactivity takes 30–60 seconds to wake up.

---

## Problem

Delhi's air pollution varies sharply by neighborhood — the industrial east can read 80 µg/m³ higher than the residential south on the same day. City-wide AQI numbers hide this. This project forecasts PM2.5 **24 hours ahead, station-by-station**, and surfaces the result as a health-categorized alert on a Delhi map.

---

## Data

| Source         | What                                                                     |
| -------------- | ------------------------------------------------------------------------ |
| OpenAQ API     | Hourly PM2.5 from 3 DPCC stations (Anand Vihar, R K Puram, Punjabi Bagh) |
| Open-Meteo API | Hourly weather — temperature, humidity, wind, precipitation              |

**Coverage:** April 5 – June 2, 2026 (~59 days, pre-monsoon).

---

## Methodology

- **Features:** PM2.5 lags (1, 3, 6, 24h), rolling averages (3, 6, 12h, all `shift(1)`-guarded against leakage), weather variables, time-of-day/week/month flags.
- **Target:** PM2.5 24 hours ahead, per station.
- **Split:** Chronological, per station (first 80% train, last 20% test).
- **Baseline:** Persistence (predict tomorrow = today). Strong on autocorrelated pollution data.
- **Model:** Regularized XGBoost, one per station. Hyperparameters tuned to fight an initial 20-unit train/test overfit gap.

---

## Results

| Station      | Baseline MAE | XGBoost MAE | Improvement |
| ------------ | -----------: | ----------: | ----------: |
| Anand Vihar  |        32.90 |   **28.89** |   **+4.01** |
| R K Puram    |        25.58 |   **23.85** |   **+1.73** |
| Punjabi Bagh |        20.96 |       22.04 |       −1.08 |

Values in µg/m³. XGBoost adds clear value at volatile stations and modest value at moderately variable ones; at Punjabi Bagh persistence is already near-optimal and the model marginally underperforms.

---

## Limitations

- **Single-season data** (April–June). Model has not seen Delhi's winter 200–400 µg/m³ regime.
- **Spike under-prediction.** Model regresses toward the mean and undershoots sharp peaks — exactly the regime that matters most for health alerts.
- The dashboard's "latest forecast" is the model's prediction on the final test-window timestamp, not a live forecast for actual tomorrow.

---

## Future Work

1. Extend training to Delhi's winter pollution season (highest-impact change).
2. Spike-aware loss (quantile or asymmetric) to prioritize high-pollution forecasts.
3. Live inference pipeline pulling trailing 24h from OpenAQ + Open-Meteo on a schedule.

---

## Tech Stack

Python, pandas, XGBoost, scikit-learn, Plotly Dash, gunicorn, Render.

---

## Local Setup

```bash
git clone https://github.com/virajapalleti/hyperlocal-aqi-forecaster.git
cd hyperlocal-aqi-forecaster

python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows
# source venv/bin/activate      # macOS/Linux

pip install -r requirements.txt
python app.py
```

App runs at `http://127.0.0.1:8050/`.
