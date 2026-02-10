import os
from dotenv import load_dotenv
from pandas import DataFrame
import datetime
from io import StringIO
import psycopg2

load_dotenv('/home/dinzhir/PycharmProjects/WeatherGuru/data_db.env')
conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT')
)

cursor_spb = conn.cursor()
cursor_spb.execute("""
SELECT temperature, wind_speed, humidity, absolute_humidity, 
       atmosphere_pressure, uv, aqi, no2, so2, o3, co, pm10, pm2_5, 
       magnetic_storms, pollen, solar_w_speed, solar_w_density, 
       bz, tested_influenza, inf_influenza, tested_arvi, inf_arvi, 
       tested_covid19, inf_covid19, magnetic_hazard 
FROM data_weather_saint_petersburg
""")

cursor_msk = conn.cursor()
cursor_msk.execute("""
SELECT temperature, wind_speed, humidity, absolute_humidity, 
       atmosphere_pressure, uv, aqi, no2, so2, o3, co, pm10, pm2_5, 
       magnetic_storms, pollen, solar_w_speed, solar_w_density, 
       bz, tested_influenza, inf_influenza, tested_arvi, inf_arvi, 
       tested_covid19, inf_covid19, magnetic_hazard 
FROM data_weather_moscow
""")

rows_spb = cursor_spb.fetchall()
rows_msk = cursor_msk.fetchall()

print(f"Найдено записей Санкт-Петербург: {len(rows_spb)}")
print(f"Найдено записей Москва: {len(rows_msk)}")

cursor_spb.close()
cursor_msk.close()
conn.close()

Temp_Saint_Petersburg, Wind_s_Saint_Petersburg, Humid_Saint_Petersburg, AHumid_Saint_Petersburg, Apress_Saint_Petersburg, UV_Saint_Petersburg, AQI_Saint_Petersburg, NO2_Saint_Petersburg, SO2_Saint_Petersburg, O3_Saint_Petersburg, CO_Saint_Petersburg, PM10_Saint_Petersburg, PM2_5_Saint_Petersburg, Magnetic_s_Saint_Petersburg, Pollen_Saint_Petersburg, Solar_s_Saint_Petersburg, Solar_w_Saint_Petersburg, Bz_Saint_Petersburg, Tested_inf_Saint_Petersburg, Inf_inf_Saint_Petersburg, Tested_ARVI_Saint_Petersburg, Inf_ARVI_Saint_Petersburg, Tested_COVID_Saint_Petersburg, Inf_COVID_Saint_Petersburg, Magnetic_hazard_Saint_Petersburg = rows_spb[-1]

Temp_Moscow, Wind_s_Moscow, Humid_Moscow, AHumid_Moscow, Apress_Moscow, UV_Moscow, AQI_Moscow, NO2_Moscow, SO2_Moscow, O3_Moscow, CO_Moscow, PM10_Moscow, PM2_5_Moscow, Magnetic_s_Moscow, Pollen_Moscow, Solar_s_Moscow, Solar_w_Moscow, Bz_Moscow, Tested_inf_Moscow, Inf_inf_Moscow, Tested_ARVI_Moscow, Inf_ARVI_Moscow, Tested_COVID_Moscow, Inf_COVID_Moscow, Magnetic_hazard_Moscow = rows_msk[-1]

def temperature_risk(temp):
    if 18 <= temp <= 24:
        return 0.0, temp/abs(temp)
    elif 14 <= temp <= 28:
        return 0.2, temp/abs(temp)
    elif -15 <= temp <= 35:
        return 0.5, temp/abs(temp)
    else:
        deviation = min(abs(temp - 21), 30)
        return min(0.5 + (deviation ** 2) / 900, 1.0), temp/abs(temp)

def wind_speed_risk(wind):
    if wind <= 19.44:
        return 0.0
    elif wind <= 38.52:
        return 0.3
    elif wind <= 61.56:
        return 0.6
    else:
        return min(0.6 + (wind - 61.56) / 180, 1.0)

def relative_humidity_risk(humidity):
    if 40 <= humidity <= 60:
        return 0.0
    elif 30 <= humidity <= 70:
        return 0.2
    elif 20 <= humidity <= 80:
        return 0.4
    else:
        deviation = min(abs(humidity - 50), 50)
        return min(0.4 + deviation / 125, 1.0)

def absolute_humidity_risk(abs_humidity):
    if 4 <= abs_humidity <= 12:
        return 0.0
    elif 2 <= abs_humidity <= 18:
        return 0.4
    else:
        deviation = min(abs(abs_humidity - 8), 20)
        return min(0.4 + deviation / 50, 1.0)

def pressure_risk(pressure):
    deviation = abs(pressure - 760)
    if deviation <= 10:
        return 0.0
    elif deviation <= 20:
        return 0.2
    elif deviation <= 40:
        return 0.5
    else:
        return min(0.5 + (deviation - 40) / 120, 1.0)

def uv_index_risk(uv_index):
    if uv_index <= 2:
        return 0.0
    elif uv_index <= 5:
        return 0.3
    elif uv_index <= 7:
        return 0.6
    elif uv_index <= 10:
        return 0.8
    else:
        return 1.0

def aqi_risk(aqi):
    if aqi <= 50:
        return 0.0
    elif aqi <= 100:
        return 0.3
    elif aqi <= 150:
        return 0.6
    elif aqi <= 200:
        return 0.8
    elif aqi <= 300:
        return 0.9
    else:
        return 1.0

def no2_risk(no2):
    if no2 <= 40:
        return 0.0
    elif no2 <= 80:
        return 0.3
    elif no2 <= 120:
        return 0.6
    elif no2 <= 200:
        return 0.8
    else:
        return 1.0

def so2_risk(so2):
    if so2 <= 40:
        return 0.0
    elif so2 <= 80:
        return 0.4
    elif so2 <= 200:
        return 0.7
    elif so2 <= 500:
        return 0.9
    else:
        return 1.0

def ozone_risk(o3):
    if o3 <= 40:
        return 0.0
    elif o3 <= 70:
        return 0.5
    elif o3 <= 100:
        return 0.8
    else:
        return 1.0

def co_risk(co_):
    if co_ <= 300:
        return 0.0
    elif co_ <= 1000:
        return 0.3
    elif co_ <= 2000:
        return 0.5
    elif co_ <= 5000:
        return 0.7
    elif co_ <= 10000:
        return 0.9
    else:
        return 1.0

def pm10_risk(pm10):
    if pm10 <= 15:
        return 0.0
    elif pm10 <= 30:
        return 0.3
    elif pm10 <= 50:
        return 0.6
    elif pm10 <= 100:
        return 0.8
    else:
        return 1.0

def pm25_risk(pm25):
    if pm25 <= 5:
        return 0.0
    elif pm25 <= 10:
        return 0.4
    elif pm25 <= 25:
        return 0.7
    elif pm25 <= 50:
        return 0.9
    else:
        return 1.0

def magnetic_storm_risk(kp_index):
    if kp_index < 4:
        return 0.0
    elif kp_index < 5:
        return 0.3
    elif kp_index < 6:
        return 0.6
    elif kp_index < 7:
        return 0.8
    else:
        return 1.0

def pollen_risk(pollen_level):
    if pollen_level == 'не\xa0активна':
        return 0.0
    return 1.0

def solar_wind_speed_risk(speed_kms):
    if speed_kms <= 400:
        return 0.0
    elif speed_kms <= 600:
        return 0.4
    elif speed_kms <= 800:
        return 0.7
    else:
        return min(0.7 + (speed_kms - 800) / 1000, 1.0)

def solar_wind_density_risk(density_ppcm3):
    if density_ppcm3 <= 10:
        return 0.0
    elif density_ppcm3 <= 30:
        return 0.7
    else:
        return min(0.7 + (density_ppcm3 - 30) / 200, 1.0)

def bz_component_risk(bz_nt):
    if bz_nt >= -5:
        return 0.0
    elif bz_nt >= -10:
        return 0.5
    else:
        return 1.0

def influenza(t,i):
    q=i/t
    if q<=0.1:
        return 0.3
    elif q<=0.2:
        return 0.7
    return 1

def arvi(t,i):
    q=i/t
    if q<=0.04:
        return 0
    if q<=0.1:
        return 0.3
    elif q<=0.17:
        return 0.7
    return 1

def covid19(t,i):
    q=i/t
    if q<=0.02:
        return 0
    elif q<=0.08:
        return 0.5
    elif q<=0.14:
        return 0.7
    return 1

def magnetic_storm_hazard(level):
    if level=='низкий':
        return 0
    elif level=='средний':
        return 0.5
    return 1

temperature_risk_Saint_Petersburg = temperature_risk(Temp_Saint_Petersburg)
wind_speed_risk_Saint_Petersburg = wind_speed_risk(Wind_s_Saint_Petersburg)
relative_humidity_risk_Saint_Petersburg = relative_humidity_risk(Humid_Saint_Petersburg)
absolute_humidity_risk_Saint_Petersburg = absolute_humidity_risk(AHumid_Saint_Petersburg)
pressure_risk_Saint_Petersburg = pressure_risk(Apress_Saint_Petersburg)
uv_index_risk_Saint_Petersburg = uv_index_risk(UV_Saint_Petersburg)
aqi_risk_Saint_Petersburg = aqi_risk(AQI_Saint_Petersburg)
no2_risk_Saint_Petersburg = no2_risk(NO2_Saint_Petersburg)
so2_risk_Saint_Petersburg = so2_risk(SO2_Saint_Petersburg)
ozone_risk_Saint_Petersburg = ozone_risk(O3_Saint_Petersburg)
co_risk_Saint_Petersburg = co_risk(CO_Saint_Petersburg)
pm10_risk_Saint_Petersburg = pm10_risk(PM10_Saint_Petersburg)
pm25_risk_Saint_Petersburg = pm25_risk(PM2_5_Saint_Petersburg)
magnetic_storm_risk_Saint_Petersburg = magnetic_storm_risk(Magnetic_s_Saint_Petersburg)
pollen_risk_Saint_Petersburg = pollen_risk(Pollen_Saint_Petersburg)
solar_wind_speed_risk_Saint_Petersburg = solar_wind_speed_risk(Solar_s_Saint_Petersburg)
solar_wind_density_risk_Saint_Petersburg = solar_wind_density_risk(Solar_w_Saint_Petersburg)
bz_component_risk_Saint_Petersburg = bz_component_risk(Bz_Saint_Petersburg)
influenza_Saint_Petersburg = influenza(Tested_inf_Saint_Petersburg, Inf_inf_Saint_Petersburg)
ARVI_Saint_Petersburg = arvi(Tested_ARVI_Saint_Petersburg, Inf_ARVI_Saint_Petersburg)
COVID19_Saint_Petersburg = covid19(Tested_COVID_Saint_Petersburg, Inf_COVID_Saint_Petersburg)
Magnetic_storm_hazard_Saint_Petersburg = magnetic_storm_hazard(Magnetic_hazard_Saint_Petersburg)

temperature_risk_Moscow = temperature_risk(Temp_Moscow)
wind_speed_risk_Moscow = wind_speed_risk(Wind_s_Moscow)
relative_humidity_risk_Moscow = relative_humidity_risk(Humid_Moscow)
absolute_humidity_risk_Moscow = absolute_humidity_risk(AHumid_Moscow)
pressure_risk_Moscow = pressure_risk(Apress_Moscow)
uv_index_risk_Moscow = uv_index_risk(UV_Moscow)
aqi_risk_Moscow = aqi_risk(AQI_Moscow)
no2_risk_Moscow = no2_risk(NO2_Moscow)
so2_risk_Moscow = so2_risk(SO2_Moscow)
ozone_risk_Moscow = ozone_risk(O3_Moscow)
co_risk_Moscow = co_risk(CO_Moscow)
pm10_risk_Moscow = pm10_risk(PM10_Moscow)
pm25_risk_Moscow = pm25_risk(PM2_5_Moscow)
magnetic_storm_risk_Moscow = magnetic_storm_risk(Magnetic_s_Moscow)
pollen_risk_Moscow = pollen_risk(Pollen_Moscow)
solar_wind_speed_risk_Moscow = solar_wind_speed_risk(Solar_s_Moscow)
solar_wind_density_risk_Moscow = solar_wind_density_risk(Solar_w_Moscow)
bz_component_risk_Moscow = bz_component_risk(Bz_Moscow)
influenza_Moscow = influenza(Tested_inf_Moscow, Inf_inf_Moscow)
ARVI_Moscow = arvi(Tested_ARVI_Moscow, Inf_ARVI_Moscow)
COVID19_Moscow = covid19(Tested_COVID_Moscow, Inf_COVID_Moscow)
Magnetic_storm_hazard_Moscow = magnetic_storm_hazard(Magnetic_hazard_Moscow)

diff_pressure_Saint_Petersburg = abs(rows_spb[-1][4]-rows_spb[-2][4])
diff_temp_Saint_Petersburg = abs(rows_spb[-1][0]-rows_spb[-2][0])
data_temp_Saint_Petersburg = Temp_Saint_Petersburg
data_humid_Saint_Petersburg = Humid_Saint_Petersburg
data_pressure_Saint_Petersburg = Apress_Saint_Petersburg
data_wind_Saint_Petersburg = Wind_s_Saint_Petersburg

diff_pressure_Moscow = abs(rows_msk[-1][4]-rows_msk[-2][4])
diff_temp_Moscow = abs(rows_msk[-1][0]-rows_msk[-2][0])
data_temp_Moscow = Temp_Moscow
data_humid_Moscow = Humid_Moscow
data_pressure_Moscow = Apress_Moscow
data_wind_Moscow = Wind_s_Moscow

def risk_level(level):
    if level<=0.2:
        return 'низкий'
    if level<=0.4:
        return 'ниже_среднего'
    if level<=0.6:
        return 'средний'
    if level<=0.8:
        return 'высокий'
    return 'очень_высокий'

def rese(res):
    if res < 0.2:
        return 0.0
    elif res < 0.4:
        return 0.3 * (res / 0.4)
    elif res < 0.6:
        return 0.3 + 0.3 * ((res - 0.4) / 0.2)
    elif res < 0.8:
        return 0.6 + 0.2 * ((res - 0.6) / 0.2)
    else:
        return 0.8 + 0.2 * ((res - 0.8) / 0.2)

def arterial_hypertension(temp, humidity, pressure, magnetic_s):
    if temp[1]>0:
        temp_val=temp[0]
    else:
        temp_val=0
    weights = {
        'pressure': 0.4,
        'magnetic': 0.3,
        'temp': 0.2,
        'humidity': 0.1
    }
    res = temp_val*weights['temp']+humidity*weights['humidity']+pressure*weights['pressure']+magnetic_s*weights['magnetic']
    return risk_level(rese(res))

def ischemic_heart_disease(temp, wind, humid, aqi, magnetic):
    temp_value, temp_flag = temp
    if temp_flag < 0:
        q = temp_value + wind*2
    else:
        q = temp_value + humid * 2
    q_normalized = min(max(q, 0), 1)
    weights = {
        'temp_wind_humid': 0.5,
        'aqi': 0.3,
        'magnetic': 0.2
    }
    res = q_normalized*weights['temp_wind_humid']+aqi*weights['aqi']+magnetic*weights['magnetic']
    return risk_level(rese(res))

def chronic_heart_failure(temp, humid, pressure, no2, pm2_5):
    temp_value, temp_flag = temp
    if temp_flag > 0:
        q = temp_value + humid*2
    else:
        q = temp_value + humid
    q_normalized = min(max(q, 0), 1)
    weights = {
        'temp_humid': 0.5,
        'pressure': 0.3,
        'no2': 0.1,
        'pm2_5': 0.1
    }
    res = q_normalized*weights['temp_humid']+pressure*weights['pressure']+no2*weights['no2']+pm2_5*weights['pm2_5']
    return risk_level(rese(res))

def bronchial_astma(temp, humid, wind, aqi, pollen):
    temp_value, temp_flag = temp
    if temp_flag < 0:
        q = temp_value + wind*2
    else:
        q = temp_value + wind
    q_normalized = min(max(q, 0), 1)
    weights = {
        'temp_wind': 0.3,
        'aqi': 0.3,
        'pollen': 0.3,
        'humid':0.1
    }
    res = q_normalized*weights['temp_wind']+humid*weights['humid']+aqi*weights['aqi']+pollen*weights['pollen']
    return risk_level(rese(res))

def copd(temp, humid, aqi, influence, arvi2):
    temp_value, temp_flag = temp
    if temp_flag < 0:
        q = temp_value
    else:
        q = 0
    q_normalized = min(max(q, 0), 1)
    weights = {
        'temp': 0.2,
        'humid': 0.2,
        'aqi': 0.2,
        'influence': 0.2,
        'ARVI': 0.2
    }
    res = q_normalized*weights['temp']+humid*weights['humid']+aqi*weights['aqi']+influence*weights['influence']+arvi2*weights['ARVI']
    return risk_level(rese(res))

def allergic_rhinitis(wind, pollen, aqi, humid, data_humid):
    if wind > 0.5:
        q = wind + pollen*1.4
    else:
        q = wind+pollen
    if humid > 0.5 and data_humid > 70:
        q = q - humid*(data_humid/100)
    q_normalized = min(max(q, 0), 1)
    weights = {
        'wind_pollen': 0.6,
        'aqi': 0.2
    }
    res = q_normalized*weights['wind_pollen']+aqi*weights['aqi']
    return risk_level(rese(res))

def respiratory_infection(temp, data_humid, aqi, influence, arvi2):
    temp_value, temp_flag = temp
    if temp_flag < 0:
        q = temp_value
    else:
        q = 0
    if data_humid <= 20:
        q+=1
    elif data_humid <= 40:
        q+= 0.5
    weights = {
        'temp_humid': 0.2,
        'aqi': 0.1,
        'influence': 0.3,
        'ARVI': 0.4
    }
    res = q*weights['temp_humid']+aqi*weights['aqi']+influence*weights['influence']+arvi2*weights['ARVI']
    return risk_level(rese(res))

def osteoarthritis_arthritis(data_humid, temp, diff_pressure):
    temp_value, temp_flag = temp
    if temp_flag < 0:
        temp = temp_value
    else:
        temp = 0
    if data_humid >= 70:
        data_humid = data_humid/100
    if diff_pressure >= 30:
        diff_pressure = diff_pressure/100
    else:
        diff_pressure = 0
    weights = {
        'temp': 0.4,
        'humid': 0.4,
        'pressure': 0.2
    }
    res = temp*weights['temp']+diff_pressure*weights['pressure'] + data_humid*weights['humid']
    return risk_level(rese(res))

def old_injuries(diff_pressure):
    if diff_pressure >= 70:
        res = 1.0
    elif diff_pressure >= 60:
        res = 0.8
    elif diff_pressure >= 45:
        res = 0.6
    elif diff_pressure >= 30:
        res = 0.3
    else:
        res = 0.0
    return risk_level(rese(res))

def migraine(diff_pressure, temp, uv, data_humid, magnetic_s, wind):
    temp_value, temp_flag = temp
    if temp_flag > 0:
        q = temp_value
    else:
        q = 0
    if data_humid >= 70:
        q += data_humid/100
    diff_pressure = diff_pressure/100
    weights = {
        'UV': 0.1,
        'magnetic_s': 0.3,
        'wind': 0.2,
        'temp_humid': 0.2,
        'diff_pressure': 0.2,
    }
    res = diff_pressure*weights['diff_pressure']+uv*weights['UV']+ magnetic_s*weights['magnetic_s']+wind*weights['wind']+q*weights['temp_humid']
    return risk_level(rese(res))

def vvd(diff_pressure, diff_temp, temp, data_humid, magnetic_s):
    temp_value, temp_flag = temp
    if temp_flag > 0:
        q = temp_value
    else:
        q = 0
    diff = (diff_pressure/100+diff_temp/20)*0.5
    if data_humid >= 70:
        q += data_humid/100
    weights = {
        'temp_humid': 0.3,
        'diff': 0.4,
        'magnetic_s': 0.3
    }
    res = q*weights['temp_humid']+diff*weights['diff']+magnetic_s*weights['magnetic_s']
    return risk_level(rese(res))

def consque_stroke_brain_injury(diff_pressure, magnetic_s):
    diff_pressure = diff_pressure/100
    weights = {
        'magnetic_s': 0.5,
        'diff_pressure': 0.5
    }
    res = diff_pressure*weights['diff_pressure']+magnetic_s*weights['magnetic_s']
    return risk_level(rese(res))

def eye_pain(uv, data_humid, wind):
    if data_humid <=20:
        data_humid_val = 1
    elif data_humid <=40:
        data_humid_val = 0.5
    else:
        data_humid_val = 0
    weights = {
        'UV': 0.2,
        'data_humid': 0.4,
        'wind': 0.4
    }
    res = uv*weights['UV']+data_humid_val*weights['data_humid']+wind*weights['wind']
    return risk_level(rese(res))

def heat_stroke(uv, data_humid, data_temp, data_wind):
    if data_temp <= 27 or data_wind>9:
        return risk_level(rese(0.0))
    weights = {
        'UV': 0.5,
        'data_humid': 0.5,
    }
    res = uv*weights['UV'] + (data_humid/100)*weights['data_humid']
    return risk_level(rese(res))

def hypothermia(temp, wind, data_humid):
    temp_value, temp_flag = temp
    if temp_flag > 0:
        return risk_level(rese(0.0))
    temp_val = temp_value
    data_humid_val = data_humid/100
    weights = {
        'temp': 0.5,
        'data': 0.3,
        'wind': 0.4
    }
    res = data_humid_val*weights['data']+wind*weights['wind']+temp_val*weights['temp']
    return risk_level(rese(res))

Risk = {
    'Risks': [
        'дата',
        'город',
        'артериальная_гипертензия',
        'ишемическая_болезнь_сердца',
        'хроническая_сердечная_недостаточность',
        'бронхиальная_астма',
        'хобл',
        'аллергический_ринит',
        'респираторная_инфекция',
        'остеоартрит_артрит',
        'старые_травмы',
        'мигрень',
        'вегетососудистая_дистония',
        'последствия_инсульта_и_травмы_мозга',
        'боль_в_глазах',
        'тепловой_удар',
        'переохлаждение'
    ],
    'Saint-Petersburg': [
        datetime.datetime.now().replace(microsecond=0),
        'Saint-Petersburg',
        arterial_hypertension(temperature_risk_Saint_Petersburg, relative_humidity_risk_Saint_Petersburg, pressure_risk_Saint_Petersburg, magnetic_storm_risk_Saint_Petersburg),
        ischemic_heart_disease(temperature_risk_Saint_Petersburg, wind_speed_risk_Saint_Petersburg, relative_humidity_risk_Saint_Petersburg, aqi_risk_Saint_Petersburg, magnetic_storm_risk_Saint_Petersburg),
        chronic_heart_failure(temperature_risk_Saint_Petersburg, relative_humidity_risk_Saint_Petersburg, pressure_risk_Saint_Petersburg, no2_risk_Saint_Petersburg, pm25_risk_Saint_Petersburg),
        bronchial_astma(temperature_risk_Saint_Petersburg, relative_humidity_risk_Saint_Petersburg, wind_speed_risk_Saint_Petersburg, aqi_risk_Saint_Petersburg, pollen_risk_Saint_Petersburg),
        copd(temperature_risk_Saint_Petersburg, relative_humidity_risk_Saint_Petersburg, aqi_risk_Saint_Petersburg, influenza_Saint_Petersburg, ARVI_Saint_Petersburg),
        allergic_rhinitis(wind_speed_risk_Saint_Petersburg, pollen_risk_Saint_Petersburg, aqi_risk_Saint_Petersburg, relative_humidity_risk_Saint_Petersburg, data_humid_Saint_Petersburg),
        respiratory_infection(temperature_risk_Saint_Petersburg, data_humid_Saint_Petersburg, aqi_risk_Saint_Petersburg, influenza_Saint_Petersburg, ARVI_Saint_Petersburg),
        osteoarthritis_arthritis(data_humid_Saint_Petersburg, temperature_risk_Saint_Petersburg, diff_pressure_Saint_Petersburg),
        old_injuries(diff_pressure_Saint_Petersburg),
        migraine(diff_pressure_Saint_Petersburg, temperature_risk_Saint_Petersburg, uv_index_risk_Saint_Petersburg, data_humid_Saint_Petersburg, magnetic_storm_risk_Saint_Petersburg, wind_speed_risk_Saint_Petersburg),
        vvd(diff_pressure_Saint_Petersburg, diff_temp_Saint_Petersburg, temperature_risk_Saint_Petersburg, data_humid_Saint_Petersburg, magnetic_storm_risk_Saint_Petersburg),
        consque_stroke_brain_injury(diff_pressure_Saint_Petersburg, magnetic_storm_risk_Saint_Petersburg),
        eye_pain(uv_index_risk_Saint_Petersburg, data_humid_Saint_Petersburg, wind_speed_risk_Saint_Petersburg),
        heat_stroke(uv_index_risk_Saint_Petersburg, data_humid_Saint_Petersburg, data_temp_Saint_Petersburg, data_wind_Saint_Petersburg),
        hypothermia(temperature_risk_Saint_Petersburg, wind_speed_risk_Saint_Petersburg, data_humid_Saint_Petersburg)
    ],
    'Moscow': [
        datetime.datetime.now().replace(microsecond=0),
        'Moscow',
        arterial_hypertension(temperature_risk_Moscow, relative_humidity_risk_Moscow, pressure_risk_Moscow, magnetic_storm_risk_Moscow),
        ischemic_heart_disease(temperature_risk_Moscow, wind_speed_risk_Moscow, relative_humidity_risk_Moscow, aqi_risk_Moscow, magnetic_storm_risk_Moscow),
        chronic_heart_failure(temperature_risk_Moscow, relative_humidity_risk_Moscow, pressure_risk_Moscow, no2_risk_Moscow, pm25_risk_Moscow),
        bronchial_astma(temperature_risk_Moscow, relative_humidity_risk_Moscow, wind_speed_risk_Moscow, aqi_risk_Moscow, pollen_risk_Moscow),
        copd(temperature_risk_Moscow, relative_humidity_risk_Moscow, aqi_risk_Moscow, influenza_Moscow, ARVI_Moscow),
        allergic_rhinitis(wind_speed_risk_Moscow, pollen_risk_Moscow, aqi_risk_Moscow, relative_humidity_risk_Moscow, data_humid_Moscow),
        respiratory_infection(temperature_risk_Moscow, data_humid_Moscow, aqi_risk_Moscow, influenza_Moscow, ARVI_Moscow),
        osteoarthritis_arthritis(data_humid_Moscow, temperature_risk_Moscow, diff_pressure_Moscow),
        old_injuries(diff_pressure_Moscow),
        migraine(diff_pressure_Moscow, temperature_risk_Moscow, uv_index_risk_Moscow, data_humid_Moscow, magnetic_storm_risk_Moscow, wind_speed_risk_Moscow),
        vvd(diff_pressure_Moscow, diff_temp_Moscow, temperature_risk_Moscow, data_humid_Moscow, magnetic_storm_risk_Moscow),
        consque_stroke_brain_injury(diff_pressure_Moscow, magnetic_storm_risk_Moscow),
        eye_pain(uv_index_risk_Moscow, data_humid_Moscow, wind_speed_risk_Moscow),
        heat_stroke(uv_index_risk_Moscow, data_humid_Moscow, data_temp_Moscow, data_wind_Moscow),
        hypothermia(temperature_risk_Moscow, wind_speed_risk_Moscow, data_humid_Moscow)
    ]
}

df_risk = DataFrame(data=Risk)
df_risk.index = df_risk.index + 1
print(df_risk)
df_risk = df_risk.set_index('Risks')
spb_data = df_risk['Saint-Petersburg']
mos_data = df_risk['Moscow']

indicator_to_column = {
    'дата': 'date',
    'город': 'town',
    'артериальная_гипертензия': 'arterial_hypertension',
    'ишемическая_болезнь_сердца': 'ischemic_heart_disease',
    'хроническая_сердечная_недостаточность': 'chronic_heart_failure',
    'бронхиальная_астма': 'bronchial_astma',
    'хобл': 'copd',
    'аллергический_ринит': 'allergic_rhinitis',
    'респираторная_инфекция': 'respiratory_infection',
    'остеоартрит_артрит': 'osteoarthritis_arthritis',
    'старые_травмы': 'old_injuries',
    'мигрень': 'migraine',
    'вегетососудистая_дистония': 'vvd',
    'последствия_инсульта_и_травмы_мозга': 'cons_stroke_brain_injury',
    'боль_в_глазах': 'eye_pain',
    'тепловой_удар': 'heat_stroke',
    'переохлаждение': 'hypothermia'
}

insert_data = {}

for indicator, value in spb_data.items():
    if indicator in indicator_to_column:
        column_name = indicator_to_column[indicator]
        insert_data[column_name] = value

insert_data2 = {}

for indicator, value in mos_data.items():
    if indicator in indicator_to_column:
        column_name = indicator_to_column[indicator]
        insert_data2[column_name] = value

df_for_db = DataFrame([insert_data])
df_for_db2 = DataFrame([insert_data2])

sio_spb = StringIO()
sio_moscow = StringIO()

df_for_db.to_csv(sio_spb, index=False, header=False)
sio_spb.seek(0)

df_for_db2.to_csv(sio_moscow, index=False, header=False)
sio_moscow.seek(0)

load_dotenv('/home/dinzhir/PycharmProjects/WeatherGuru/data_db.env')
connection = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT')
)

with connection.cursor() as co:
    columns = ', '.join(df_for_db.columns.tolist())
    co.copy_expert(
        sql=f"""
        COPY risks ({columns}) 
        FROM STDIN WITH CSV
        """,
        file=sio_spb
    )
    connection.commit()

with connection.cursor() as co:
    columns = ', '.join(df_for_db2.columns.tolist())
    co.copy_expert(
        sql=f"""
        COPY risks ({columns}) 
        FROM STDIN WITH CSV
        """,
        file=sio_moscow
    )
    connection.commit()
connection.close()