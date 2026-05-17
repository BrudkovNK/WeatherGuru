import sqlite3
import datetime
import math

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

from init_db import DB_PATH

_cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
_retry_session = retry(_cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=_retry_session)

CITIES = {
    'Saint-Petersburg': {'lat': 59.94156, 'lon': 30.314476},
    'Moscow':           {'lat': 55.75580, 'lon': 37.617300},
}

class DataWeather:
    __slots__ = [
        'temperature', 'wind_speed', 'humidity', 'absolute_humidity',
        'atm_pressure', 'uv_index', 'current_air_quality',
        'pm2_5', 'pm10', 'no2', 'co', 'so2', 'o3','alder_pollen','birch_pollen','grass_pollen','mugwort_pollen','olive_pollen','ragweed_pollen',
    ]
    def __init__(self):
        for s in self.__slots__:
            object.__setattr__(self, s, 0.0)

def _abs_humidity(humidity: float, temperature: float) -> float:
    rh = float(humidity) / 100
    t  = float(temperature)
    rv = 461.5
    a, b, c = (611.2, 18.678, 257.14) if t > 0 else (611.15, 23.036, 279.82)
    es = a * math.e ** ((b * t) / (c + t))
    return round((es * rh) / (rv * (t + 273.15)) * 1000, 4)

def _hourly_df(resp, names):
    h = resp.Hourly()
    dates = pd.date_range(
        start=pd.to_datetime(h.Time(), unit="s", utc=True),
        end=pd.to_datetime(h.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=h.Interval()),
        inclusive="left",
    )
    data = {"date": dates}
    for i, name in enumerate(names):
        data[name] = h.Variables(i).ValuesAsNumpy()
    return pd.DataFrame(data)

def _fetch_weather(lat, lon):
    names = ["temperature_2m", "relative_humidity_2m",
             "wind_speed_10m", "surface_pressure", "uv_index"]
    resp = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat, "longitude": lon, "hourly": names,
        "models": "best_match", "forecast_days": 1,
    })[0]
    return _hourly_df(resp, names)

def _fetch_air_quality(lat, lon):
    names = ["pm10", "pm2_5", "carbon_monoxide",
             "ozone", "nitrogen_dioxide", "sulphur_dioxide"]
    resp = openmeteo.weather_api("https://air-quality-api.open-meteo.com/v1/air-quality", params={
        "latitude": lat, "longitude": lon, "hourly": names, "forecast_days": 1,
    })[0]
    return _hourly_df(resp, names)

def _fetch_pollen(lat,lon):
    names = ["alder_pollen", "birch_pollen", "grass_pollen", "mugwort_pollen", "olive_pollen", "ragweed_pollen"]
    resp = openmeteo.weather_api("https://air-quality-api.open-meteo.com/v1/air-quality",params={
        "latitude": lat, "longitude": lon, "hourly": names, "forecast_days": 1,
    })[0]
    return _hourly_df(resp, names)

def _current_row(df):
    if df.empty:
        return pd.Series(dtype=float)
    now_utc = pd.Timestamp.now('UTC')
    if df['date'].dt.tz is None:
        df_dates = df['date'].dt.tz_localize('UTC')
    else:
        df_dates = df['date']
    now_utc_hour = now_utc.floor('h')
    idx = (df_dates - now_utc_hour).abs().idxmin()
    return df.loc[idx]

def _g(row, key, default=0.0):
    try:
        v = row.get(key, default)
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default

def fetch_all():
    result = {}
    for city, coords in CITIES.items():
        lat, lon = coords['lat'], coords['lon']
        wf_row = _current_row(_fetch_weather(lat, lon))
        aq_row = _current_row(_fetch_air_quality(lat, lon))
        po_row = _current_row(_fetch_pollen(lat,lon))
        dw = DataWeather()
        dw.temperature = _g(wf_row, 'temperature_2m')
        dw.wind_speed = _g(wf_row, 'wind_speed_10m')
        dw.humidity = _g(wf_row, 'relative_humidity_2m', 50.0)
        dw.atm_pressure = _g(wf_row, 'surface_pressure', 1013.0)
        dw.uv_index = _g(wf_row, 'uv_index')
        dw.absolute_humidity  = _abs_humidity(dw.humidity, dw.temperature)
        dw.pm2_5 = _g(aq_row, 'pm2_5')
        dw.pm10 = _g(aq_row, 'pm10')
        dw.no2= _g(aq_row, 'nitrogen_dioxide')
        dw.co = _g(aq_row, 'carbon_monoxide')
        dw.so2 = _g(aq_row, 'sulphur_dioxide')
        dw.o3= _g(aq_row, 'ozone')
        dw.current_air_quality = round(dw.pm2_5 * 4, 1)
        dw.alder_pollen = _g(po_row,'alder_pollen')
        dw.birch_pollen = _g(po_row,'birch_pollen')
        dw.grass_pollen = _g(po_row,'grass_pollen')
        dw.mugwort_pollen = _g(po_row,'mugwort_pollen')
        dw.olive_pollen = _g(po_row,'olive_pollen')
        dw.ragweed_pollen = _g(po_row,'ragweed_pollen')
        result[city] = dw
    return result['Saint-Petersburg'], result['Moscow']

def save_weather(city_obj, table):
    now = datetime.datetime.now().replace(microsecond=0).isoformat()
    row = (
        now,
        city_obj.temperature, city_obj.wind_speed, city_obj.humidity,
        city_obj.absolute_humidity, city_obj.atm_pressure, city_obj.uv_index,
        city_obj.current_air_quality, city_obj.no2, city_obj.so2, city_obj.o3,
        city_obj.co, city_obj.pm10, city_obj.pm2_5, city_obj.alder_pollen, city_obj.birch_pollen, city_obj.grass_pollen,
        city_obj.mugwort_pollen, city_obj.olive_pollen, city_obj.ragweed_pollen,
    )
    conn = sqlite3.connect(DB_PATH)
    conn.execute(f'INSERT INTO {table} VALUES ({",".join(["?"]*len(row))})', row)
    conn.commit()
    conn.close()

def main():
    spb, mos = fetch_all()
    save_weather(spb, 'data_weather_saint_petersburg')
    save_weather(mos, 'data_weather_moscow')
    print("Погода сохранена.")

if __name__ == '__main__':
    main()
