import sqlite3
import datetime
from flask import Flask, render_template, request, jsonify
from init_db import DB_PATH, init_db, DISEASES

app = Flask(__name__)
init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.template_filter('safe_round')
def safe_round_filter(value, precision=1):
    try:
        return round(float(value), precision)
    except (TypeError, ValueError):
        return '—'

@app.route('/download_db')
def download_db():
    from flask import send_file
    return send_file('weather.db', as_attachment=True, download_name='weather.db')

@app.route('/')
def index():
    conn = get_db()
    spb_risks   = conn.execute("SELECT * FROM risks WHERE town='Saint-Petersburg' ORDER BY date DESC LIMIT 1").fetchone()
    mos_risks   = conn.execute("SELECT * FROM risks WHERE town='Moscow' ORDER BY date DESC LIMIT 1").fetchone()
    spb_weather = conn.execute("SELECT * FROM data_weather_saint_petersburg ORDER BY date DESC LIMIT 1").fetchone()
    mos_weather = conn.execute("SELECT * FROM data_weather_moscow ORDER BY date DESC LIMIT 1").fetchone()
    conn.close()
    return render_template(
        'index.html',
        spb_risks   = dict(spb_risks)   if spb_risks   else {},
        mos_risks   = dict(mos_risks)   if mos_risks   else {},
        spb_weather = dict(spb_weather) if spb_weather else {},
        mos_weather = dict(mos_weather) if mos_weather else {},
        diseases    = DISEASES,
    )

@app.route('/vote', methods=['POST'])
def vote():
    data      = request.get_json()
    city      = data.get('city')
    device_id = data.get('device_id', '')
    answers   = data.get('answers', {})

    conn = get_db()

    today = datetime.date.today().isoformat()
    exists = conn.execute(
        "SELECT id FROM votes WHERE city=? AND device_id=? AND date LIKE ?",
        (city, device_id, today + '%')
    ).fetchone()
    if exists:
        conn.close()
        return jsonify({'status': 'already_voted'})

    table = 'data_weather_saint_petersburg' if city == 'Saint-Petersburg' else 'data_weather_moscow'
    weather = conn.execute(f'SELECT * FROM {table} ORDER BY date DESC LIMIT 1').fetchone()

    if weather:
        w = dict(weather)
        disease_vals = [answers.get(d, 'нет болезни') for d in DISEASES]
        disease_placeholders = ','.join(['?'] * len(DISEASES))
        disease_cols = ','.join(DISEASES)
        conn.execute(
            f'''INSERT INTO votes (
                date, city, device_id,
                {disease_cols},
                temperature, wind_speed, humidity, absolute_humidity,
                atm_pressure, uv_index, current_air_quality,
                no2, so2, o3, co, pm10, pm2_5, , alder_pollen, birch_pollen, grass_pollen, mugwort_pollen,
                olive_pollen, ragweed_pollen
            ) VALUES (?,?,?,{disease_placeholders},?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (
                datetime.datetime.now().isoformat(), city, device_id,
                *disease_vals,
                w.get('temperature'), w.get('wind_speed'), w.get('humidity'),
                w.get('absolute_humidity'), w.get('atm_pressure'), w.get('uv_index'),
                w.get('current_air_quality'), w.get('no2'), w.get('so2'),
                w.get('o3'), w.get('co'), w.get('pm10'), w.get('pm2_5'), w.get('alder_pollen'), w.get('birch_pollen'),
                w.get('grass_pollen'), w.get('mugwort_pollen'), w.get('olive_pollen'), w.get('ragweed_pollen'),
            )
        )
        conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})
