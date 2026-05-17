import sqlite3
import datetime
from init_db import DB_PATH
import numpy as np

def temperature_risk(temp):
    if temp == 0: return 0.0, 1
    if 18 <= temp <= 24: return 0.0, temp / abs(temp)
    if 14 <= temp <= 28: return 0.2, temp / abs(temp)
    if -15 <= temp <= 35: return 0.5, temp / abs(temp)
    deviation = min(abs(temp - 21), 30)
    return min(0.5 + (deviation ** 2) / 900, 1.0), temp / abs(temp)

def wind_speed_risk(w):
    if w <= 19.44: return 0.0
    if w <= 38.52: return 0.3
    if w <= 61.56: return 0.6
    return min(0.6 + (w - 61.56) / 180, 1.0)

def relative_humidity_risk(h):
    if 40 <= h <= 60: return 0.0
    if 30 <= h <= 70: return 0.2
    if 20 <= h <= 80: return 0.4
    return min(0.4 + min(abs(h - 50), 50) / 125, 1.0)

def absolute_humidity_risk(ah):
    if 4 <= ah <= 12: return 0.0
    if 2 <= ah <= 18: return 0.4
    return min(0.4 + min(abs(ah - 8), 20) / 50, 1.0)

def pressure_risk(p):
    d = abs(p - 1013)
    if d <= 10: return 0.0
    if d <= 20: return 0.2
    if d <= 40: return 0.5
    return min(0.5 + (d - 40) / 120, 1.0)

def uv_index_risk(uv):
    if uv <= 2: return 0.0
    if uv <= 5: return 0.3
    if uv <= 7: return 0.6
    if uv <= 10:  return 0.8
    return 1.0

def aqi_risk(aqi):
    if aqi <= 50: return 0.0
    if aqi <= 100:  return 0.3
    if aqi <= 150:  return 0.6
    if aqi <= 200:  return 0.8
    if aqi <= 300:  return 0.9
    return 1.0

def no2_risk(v):
    if v <= 40:  return 0.0
    if v <= 80:  return 0.3
    if v <= 120: return 0.6
    if v <= 200: return 0.8
    return 1.0

def so2_risk(v):
    if v <= 40: return 0.0
    if v <= 80: return 0.4
    if v <= 200: return 0.7
    if v <= 500: return 0.9
    return 1.0

def ozone_risk(v):
    if v <= 40: return 0.0
    if v <= 70: return 0.5
    if v <= 100: return 0.8
    return 1.0

def co_risk(v):
    if v <= 300: return 0.0
    if v <= 1000: return 0.3
    if v <= 2000: return 0.5
    if v <= 5000: return 0.7
    if v <= 10000: return 0.9
    return 1.0

def pm10_risk(v):
    if v <= 15: return 0.0
    if v <= 30: return 0.3
    if v <= 50: return 0.6
    if v <= 100: return 0.8
    return 1.0

def pm25_risk(v):
    if v <= 5: return 0.0
    if v <= 10: return 0.4
    if v <= 25: return 0.7
    if v <= 50: return 0.9
    return 1.0

def pollen(v):
    if v <= 10: return 0.0
    if v <= 30: return 0.4
    if v <= 50: return 0.7
    if v <= 100: return 0.9
    return 1.0

def rese(res):
    if res < 0.2: return 0.0
    if res < 0.4: return 0.3 * (res / 0.4)
    if res < 0.6: return 0.3 + 0.3 * ((res - 0.4) / 0.2)
    if res < 0.8: return 0.6 + 0.2 * ((res - 0.6) / 0.2)
    return 0.8 + 0.2 * ((res - 0.8) / 0.2)

def risk_label(v):
    if v <= 0.2: return 'низкий'
    if v <= 0.4: return 'ниже среднего'
    if v <= 0.6: return 'средний'
    if v <= 0.85: return 'высокий'
    return 'очень высокий'

def arterial_hypertension(temp, pressure, pm2, n2, s2, o3):
    tv = temp[0] if temp[1] > 0 else 0
    return risk_label(rese(tv * 0.5 + 0.3 * np.mean([pm2, n2, s2, o3]) + pressure * 0.2))

def ischemic_heart_disease(temp, wind, humid, aqi):
    tv, tf = temp
    q = min(max((tv + wind if tf < 0 else tv + humid), 0), 1)
    return risk_label(rese(q * 0.6 + aqi * 0.4))

def chronic_heart_failure(temp, diff, no2, pm2_5):
    tv, tf = temp
    return risk_label(rese(tv * 0.3 + diff * 0.3 + no2 * 0.2 + pm2_5 * 0.2))

def bronchial_astma(temp, humid, wind, aqi):
    tv, tf = temp
    q = min(max((tv + wind * 2 if tf < 0 else tv + wind), 0), 1)
    return risk_label(rese(q * 0.3 + humid * 0.3 + aqi * 0.4))

def copd(temp, humid, aqi):
    tv, tf = temp
    q = min(max(tv + humid if tf < 0 else 0, 0), 1)
    return risk_label(rese(q * 0.3 + humid * 0.3 + aqi * 0.4))

def allergic_rhinitis(wind, aqi, humid, al, bi, gr, mu, ol, ra):
    q = wind if wind > 0.5 else wind * 0.7
    if humid > 0.5:
        q -= humid * 0.2
    return risk_label(rese(min(max(q, 0), 1) * 0.2 + np.mean([al, bi, gr, mu, ol, ra])**(1/2) * 0.7 + aqi * 0.1))

def respiratory_infection(temp, data_humid, aqi):
    tv, tf = temp
    q = tv if tf < 0 else 0
    if data_humid <= 20: q += 1
    elif data_humid <= 40: q += 0.5
    return risk_label(rese(q * 0.7 + aqi * 0.3))

def osteoarthritis_arthritis(data_humid, temp, diff_pressure):
    tv, tf = temp
    t  = tv if tf < 0 else 0
    dh = data_humid / 100 if data_humid >= 70 else 0
    dp = diff_pressure / 100 if diff_pressure >= 30 else 0
    return risk_label(rese(t * 0.4 + dh * 0.4 + dp * 0.2))

def old_injuries(diff_pressure):
    if diff_pressure >= 70: res = 1.0
    elif diff_pressure >= 60: res = 0.8
    elif diff_pressure >= 45: res = 0.6
    elif diff_pressure >= 30: res = 0.3
    else: res = 0.0
    return risk_label(rese(res))

def migraine(diff_pressure, temp, uv, data_humid, wind):
    tv, tf = temp
    q = tv if tf > 0 else 0
    if data_humid >= 70: q += data_humid / 100
    dp = diff_pressure / 100
    return risk_label(rese(dp * 0.5 + uv * 0.2 + wind * 0.1 + q * 0.2))

def vvd(diff_pressure, diff_temp, temp, data_humid):
    tv, tf = temp
    q = tv if tf > 0 else 0
    if data_humid >= 70: q += data_humid / 100
    diff = (diff_pressure / 100 + diff_temp / 20) * 0.5
    return risk_label(rese(q * 0.2 + diff * 0.8))

def consque_stroke_brain_injury(diff_pressure):
    return risk_label(rese(diff_pressure / 100))

def eye_pain(uv, data_humid, wind):
    dh = 1 if data_humid <= 20 else (0.5 if data_humid <= 40 else 0)
    return risk_label(rese(uv * 0.2 + dh * 0.4 + wind * 0.4))

def heat_stroke(uv, data_humid, data_temp, data_wind):
    if data_temp <= 27 or data_wind > 9: return risk_label(rese(0.0))
    return risk_label(rese(uv * 0.5 + (data_humid / 100) * 0.5))

def hypothermia(temp, wind, data_humid):
    tv, tf = temp
    if tf > 0: return risk_label(rese(0.0))
    return risk_label(rese((data_humid / 100) * 0.3 + wind * 0.4 + tv * 0.5))

def _safe(val, cast=float, default=0):
    try:
        return cast(val)
    except (TypeError, ValueError):
        return default

def compute_risks(rows, city_name):
    if len(rows) < 2:
        raise ValueError("Нужно минимум 2 записи в таблице погоды")
    last, prev = rows[-1], rows[-2]

    temp = _safe(last[1])
    wind = _safe(last[2])
    humid = _safe(last[3])
    ahumid = _safe(last[4])
    press = _safe(last[5])
    uv = _safe(last[6])
    aqi = _safe(last[7])
    no2 = _safe(last[8])
    so2_v = _safe(last[9])
    o3 = _safe(last[10])
    co = _safe(last[11])
    pm10 = _safe(last[12])
    pm2_5  = _safe(last[13])
    al_po = _safe(last[14])
    bi_po = _safe(last[15])
    gr_po = _safe(last[16])
    mu_po = _safe(last[17])
    ol_po = _safe(last[18])
    ra_po = _safe(last[19])
    diff_p = abs(_safe(last[5]) - _safe(prev[5]))
    diff_t = abs(_safe(last[1]) - _safe(prev[1]))
    TR = temperature_risk(temp)
    WR = wind_speed_risk(wind)
    HR = relative_humidity_risk(humid)
    AHR = absolute_humidity_risk(ahumid)
    PR = pressure_risk(press)
    UV = uv_index_risk(uv)
    AQ = aqi_risk(aqi)
    N2 = no2_risk(no2)
    S2 = so2_risk(so2_v)
    O3 = ozone_risk(o3)
    CO = co_risk(co)
    PM10 = pm10_risk(pm10)
    PM25 = pm25_risk(pm2_5)
    AL = pollen(al_po)
    BI = pollen(bi_po)
    GR = pollen(gr_po)
    MU = pollen(mu_po)
    OL = pollen(ol_po)
    RA = pollen(ra_po)
    now = datetime.datetime.now().replace(microsecond=0).isoformat()
    return (
        now, city_name,
        arterial_hypertension(TR, PR, PM25, N2, S2, O3),
        ischemic_heart_disease(TR, WR, HR, AQ),
        chronic_heart_failure(TR, diff_t, N2, PM25),
        bronchial_astma(TR, HR, WR, AQ),
        copd(TR, HR, AQ),
        allergic_rhinitis(WR, AQ, HR, AL, BI, GR, MU, OL, RA),
        respiratory_infection(TR, humid, AQ),
        osteoarthritis_arthritis(humid, TR, diff_p),
        old_injuries(diff_p),
        migraine(diff_p, TR, UV, humid, WR),
        vvd(diff_p, diff_t, TR, humid),
        consque_stroke_brain_injury(diff_p),
        eye_pain(UV, humid, WR),
        heat_stroke(UV, humid, temp, wind),
        hypothermia(TR, WR, humid),
    )

def save_risks(row):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('INSERT INTO risks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', row)
    conn.commit()
    conn.close()

def main():
    from init_db import init_db
    init_db()
    conn = sqlite3.connect(DB_PATH)
    rows_spb = conn.execute('SELECT * FROM data_weather_saint_petersburg ORDER BY date').fetchall()
    rows_msk = conn.execute('SELECT * FROM data_weather_moscow ORDER BY date').fetchall()
    conn.close()
    save_risks(compute_risks(rows_spb, 'Saint-Petersburg'))
    save_risks(compute_risks(rows_msk, 'Moscow'))
    print("Риски сохранены.")

if __name__ == '__main__':
    main()
