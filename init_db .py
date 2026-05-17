import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather.db')

WEATHER_DDL = """
    date TEXT,
    temperature REAL, wind_speed REAL, humidity REAL,
    absolute_humidity REAL, atm_pressure REAL, uv_index REAL,
    current_air_quality REAL, no2 REAL, so2 REAL, o3 REAL, co REAL,
    pm10 REAL, pm2_5 REAL, alder_pollen REAL, birch_pollen REAL, grass_pollen REAL, mugwort_pollen REAL,
    olive_pollen REAL, ragweed_pollen REAL
"""

DISEASES = [
    'arterial_hypertension', 'ischemic_heart_disease', 'chronic_heart_failure',
    'bronchial_astma', 'copd', 'allergic_rhinitis', 'respiratory_infection',
    'osteoarthritis_arthritis', 'old_injuries', 'migraine',
    'vvd', 'cons_stroke_brain_injury', 'eye_pain', 'heat_stroke', 'hypothermia',
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(f'CREATE TABLE IF NOT EXISTS data_weather_saint_petersburg ({WEATHER_DDL})')
    c.execute(f'CREATE TABLE IF NOT EXISTS data_weather_moscow ({WEATHER_DDL})')

    c.execute('''CREATE TABLE IF NOT EXISTS risks (
        date TEXT, town TEXT,
        arterial_hypertension TEXT, ischemic_heart_disease TEXT,
        chronic_heart_failure TEXT, bronchial_astma TEXT, copd TEXT,
        allergic_rhinitis TEXT, respiratory_infection TEXT,
        osteoarthritis_arthritis TEXT, old_injuries TEXT, migraine TEXT,
        vvd TEXT, cons_stroke_brain_injury TEXT, eye_pain TEXT,
        heat_stroke TEXT, hypothermia TEXT
    )''')

    disease_cols = ',\n        '.join(f'{d} TEXT DEFAULT "нет болезни"' for d in DISEASES)
    c.execute(f'''CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT, city TEXT, device_id TEXT,
        {disease_cols},
        temperature REAL, wind_speed REAL, humidity REAL,
        absolute_humidity REAL, atm_pressure REAL, uv_index REAL,
        current_air_quality REAL, no2 REAL, so2 REAL, o3 REAL, co REAL,
        pm10 REAL, pm2_5 REAL, alder_pollen REAL, birch_pollen REAL, grass_pollen REAL, mugwort_pollen REAL,
        olive_pollen REAL, ragweed_pollen REAL
    )''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("БД инициализирована.")