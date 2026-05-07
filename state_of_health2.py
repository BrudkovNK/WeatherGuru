import pandas as pd
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import os
from dotenv import load_dotenv

#Functiom
def identify_distribution(data, alpha=0.05):
    results = {}
    #Normal
    _, p_normal = stats.normaltest(data)
    results['normal'] = p_normal
    #Exponent
    _, p_exp = stats.kstest(data, 'expon', args=(0, data.std()))
    results['exponential'] = p_exp
    #Lognorm
    _, p_lognorm = stats.kstest(data, 'lognorm',
                                args=(1, 0, data.std()))
    results['lognormal'] = p_lognorm
    #Uniform
    _, p_uniform = stats.kstest(data, 'uniform',
                                args=(data.min(), data.max()))
    results['uniform'] = p_uniform
    #Laplace
    _, p_laplace = stats.kstest(data, 'laplace',
                                args=(0, data.std()))
    results['laplace'] = p_laplace
    best_dist = max(results, key=results.get)
    return best_dist, results

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

columns = ['temperature', 'wind_speed', 'humidity', 'absolute_humidity',
       'atmosphere_pressure', 'uv', 'aqi', 'no2', 'so2', 'o3', 'co', 'pm10', 'pm2_5',
       'magnetic_storms', 'pollen', 'solar_w_speed', 'solar_w_density',
       'bz', 'tested_influenza', 'inf_influenza', 'tested_arvi', 'inf_arvi',
       'tested_covid19', 'inf_covid19', 'magnetic_hazard' ]

rows_spb = pd.DataFrame(rows_spb, columns = columns)
rows_msk = pd.DataFrame(rows_msk, columns = columns)
for i in range(len(columns)):
    rows_spb.iloc[:,i] = rows_spb.iloc[:,i].fillna(rows_spb.iloc[:,i].mode())
    rows_msk.iloc[:,i] = rows_msk.iloc[:,i].fillna(rows_msk.iloc[:,i].mode())

rows_spb.loc[rows_spb['pollen']=='не активна','pollen'] = -1
rows_spb.loc[rows_spb['pollen']!='не активна','pollen'] = 1
rows_spb.loc[rows_spb['magnetic_hazard']=='низкий','magnetic_hazard'] = 1
rows_spb.loc[rows_spb['magnetic_hazard']=='средний','magnetic_hazard'] = 2
rows_spb.loc[rows_spb['magnetic_hazard']=='высокий','magnetic_hazard'] = 3

rows_msk.loc[rows_msk['pollen']=='не активна', 'pollen'] = -1
rows_msk.loc[rows_msk['pollen']!='не активна', 'pollen'] = 1
rows_msk.loc[rows_msk['magnetic_hazard']=='низкий','magnetic_hazard'] = 1
rows_msk.loc[rows_msk['magnetic_hazard']=='средний','magnetic_hazard'] = 2
rows_msk.loc[rows_msk['magnetic_hazard']=='высокий','magnetic_hazard'] = 3

for i in range(len(columns)):
    try:
        rows_spb.iloc[:,i] -= rows_spb.iloc[:,i].mean()
    except TypeError:
        pass
    try:
        rows_msk.iloc[:,i] -= rows_msk.iloc[:,i].mean()
    except TypeError:
        pass
    try:
        rows_spb.iloc[:,i] /= rows_spb.iloc[:,i].std()
    except ZeroDivisionError:
        print(columns[i], 'имеет нулевую дисперсию в СПб')
    try:
        rows_msk.iloc[:,i] /= rows_msk.iloc[:,i].std()
    except ZeroDivisionError:
        print(columns[i], 'имеет нулевую дисперсию в МСК')

for col in rows_spb.columns:
    lower = rows_spb[col].quantile(0.02)
    upper = rows_spb[col].quantile(0.98)
    rows_spb = rows_spb[(rows_spb[col] >= lower) & (rows_spb[col] <= upper)]

for col in rows_msk.columns:
    lower = rows_msk[col].quantile(0.02)
    upper = rows_msk[col].quantile(0.98)
    rows_msk = rows_msk[(rows_msk[col] >= lower) & (rows_msk[col] <= upper)]

#Реализация наивного Байеса