# WeatherGuru
WeatherGuru is a research project studying the relationship between weather conditions and human well-being across different medical conditions.

## What it does
The application collects hourly weather and air quality data for Saint Petersburg and Moscow, calculates risk levels for 15 medical conditions, and displays them in a clean web interface. Users can provide feedback on whether the forecast matched their actual well-being — this data is the core of the project.
The long-term goal is to accumulate enough labeled data to train a predictive model that tells people with specific conditions what kind of day to expect based on the current weather.

## Conditions tracked
Arterial hypertension, Ischemic heart disease, Chronic heart failure, Bronchial asthma, COPD · Allergic rhinitis, Respiratory infection, Osteoarthritis, Old injuries, Migraine, VVD,  Post-stroke/TBI, Eye pain, Heat stroke, Hypothermia

## Stack
- Python 3.10+
- Flask
- SQLite
- open-meteo-requests / pandas
- numpy
- HTML

## Status
Version 1.0 — data collection phase. The prediction model will follow once sufficient data is gathered.
Live: [dinzhir.pythonanywhere.com](https://dinzhir.pythonanywhere.com)
