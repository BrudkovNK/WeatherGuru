from urllib.error import HTTPError
import requests
import bs4
from pandas import DataFrame
import math
from urllib3.exceptions import RequestError
from io import StringIO
import psycopg2
import os
from dotenv import load_dotenv
import datetime

def absolute_humidity_arden_bakk(humidity, temperature):
    humidity = int(humidity) / 100
    temperature = int(temperature)
    a = 611.2
    b = 18.678
    c = 257.14
    r_v = 461.5
    if temperature > 0:
        return round(((humidity * a * (math.e ** ((b * temperature) / (c + temperature)))) / (r_v * (temperature + 273.15))) * 1000, 4)
    else:
        a = 611.15
        b = 23.036
        c = 279.82
        e_s = (a * math.e ** ((b * temperature) / (c + temperature)))
        return round((e_s * humidity) / (r_v * (temperature + 273.15)) * 1000, 4)

def request(url,header):
    try:
        response = requests.get(url, timeout=3, headers=header)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except TimeoutError as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except RequestError as req_err:
        print(f"Unexpected error occurred: {req_err}")

def magnetic_storm_forecasts(solar_wind_speed, solar_wind_density, component_bz):
    solar_wind_speed = float(solar_wind_speed)
    solar_wind_density = float(solar_wind_density)
    component_bz = float(component_bz)
    probability_of_storm = solar_wind_speed / 600 + solar_wind_density / 10 + component_bz / 7
    if 5.8 < probability_of_storm:
        return 'высокий'
    elif 2.7 < probability_of_storm:
        return 'средний'
    return 'низкий'

def pars_machine(url,header,name,clas):
    pars=requests.get(url, headers=header,timeout=10)
    src=pars.text
    if len(src)==0:
        return ['NULL']*8
    soup=bs4.BeautifulSoup(src, 'lxml')
    data_pars_elemets=[]
    data_pars=soup.find_all(name, class_=clas)
    for item in data_pars:
        data_pars_elemets.append(item.text)
    if len(data_pars_elemets)==0:
        return ['NULL']*8
    return data_pars_elemets

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}

Humidity_index_Saint_Petersburg = pars_machine('https://www.gismeteo.ru/weather-sankt-peterburg-4079/now/',headers,'div','item-value')[2].strip()
request('https://www.gismeteo.ru/weather-sankt-peterburg-4079/now/',headers)

UV_index_Saint_Petersburg = pars_machine('https://pogoda.ru/Russia/Saint%20Petersburg/Saint%20Petersburg__/aqi-index-kachestva-vozduha',headers,'div','value')[0].strip()
request('https://pogoda.ru/Russia/Saint%20Petersburg/Saint%20Petersburg__/aqi-index-kachestva-vozduha',headers)

Magnetic_storms_Saint_Petersburg = (pars_machine('https://xras.ru/magnetic_storms.html/saint_petersburg/',headers,'span','graph_lastdata_text')[-1].split())[-1][:-1]
request('https://xras.ru/magnetic_storms.html/saint_petersburg/',headers)

data_pollen_Saint_Petersburg = pars_machine('https://yandex.ru/pogoda/ru/saint-petersburg/allergies?lat=59.938784&lon=30.314997',headers,'span','AppAllergyWarning_title__level_clear__V9f_T')
request('https://yandex.ru/pogoda/ru/saint-petersburg/allergies?lat=59.938784&lon=30.314997',headers)

data_pollution_Saint_Petersburg = pars_machine('https://yandex.ru/pogoda/ru/saint-petersburg/pollution?lat=59.938784&lon=30.314997', headers, 'span', 'AppPollutionDetailsTitle_subTitle__value__92vLs')
Current_air_quality_Saint_Petersburg = pars_machine('https://yandex.ru/pogoda/ru/saint-petersburg/pollution?lat=59.938784&lon=30.314997',headers,'div',"AppPollutionWidgetMeter_value__LbGTW")[0]
request('https://yandex.ru/pogoda/ru/saint-petersburg/pollution?lat=59.938784&lon=30.314997',headers)

wind_speed_Saint_Petersburg = ((pars_machine('https://www.meteoblue.com/ru/погода/неделя/Санкт-Петербург_Россия_498817', headers, 'div','wind')[0]).strip()).split()[0]
request('https://www.meteoblue.com/ru/погода/неделя/Санкт-Петербург_Россия_498817',headers)

Atm_pressure_Saint_Petersburg = pars_machine('https://yandex.ru/pogoda/ru/saint-petersburg?lat=59.938786&lon=30.314997', headers,'p','AppRangeWithSpace_chart__description__a9Wnh AppRangeWithSpace_chart__description_small__nq8nx')[0].strip()
request('https://yandex.ru/pogoda/ru/saint-petersburg?lat=59.938786&lon=30.314997',headers)

Temperature_Saint_Petersburg = (pars_machine('https://www.foreca.com/ru/100498817/Saint-Petersburg-Saint-Petersburg-Russia', headers, 'div', 'temp')[0].split())[0][:-1]
request('https://www.foreca.com/ru/100498817/Saint-Petersburg-Saint-Petersburg-Russia',headers)

Humidity_index_Moscow = pars_machine('https://www.gismeteo.ru/weather-moscow-4368/now/', headers, 'div', 'item-value')[2].strip()
request('https://www.gismeteo.ru/weather-moscow-4368/now/',headers)

UV_index_Moscow = pars_machine('https://pogoda.ru/Russia/Moscow/Moscow__/weather-month', headers, 'div', 'value')[0].strip()
request('https://pogoda.ru/Russia/Moscow/Moscow__/weather-month',headers)

Magnetic_storms_Moscow = (pars_machine('https://xras.ru/magnetic_storms.html/moscow/', headers, 'span', 'graph_lastdata_text')[-1].split())[-1][:-1]
request('https://xras.ru/magnetic_storms.html/moscow/',headers)

data_pollen_Moscow = pars_machine('https://yandex.ru/pogoda/ru/moscow/allergies', headers,'span', 'AppAllergyWarning_title__level_clear__V9f_T')
request('https://yandex.ru/pogoda/ru/moscow/allergies',headers)

data_pollution_Moscow = pars_machine('https://yandex.ru/pogoda/ru/moscow/pollution', headers, 'span', 'AppPollutionDetailsTitle_subTitle__value__92vLs')
Current_air_quality_Moscow = pars_machine('https://yandex.ru/pogoda/ru/moscow/pollution', headers, 'div','AppPollutionWidgetMeter_value__LbGTW')[0]
request('https://yandex.ru/pogoda/ru/moscow/pollution',headers)

wind_speed_Moscow = ((pars_machine('https://www.meteoblue.com/ru/погода/неделя/Москва_Россия_524901', headers, 'div', 'wind')[0]).strip()).split()[0]
request('https://www.meteoblue.com/ru/погода/неделя/Москва_Россия_524901',headers)

Atm_pressure_Moscow = pars_machine('https://yandex.ru/pogoda/ru/moscow', headers, 'p', "AppRangeWithSpace_chart__description__a9Wnh AppRangeWithSpace_chart__description_small__nq8nx")[0].strip()
request('https://yandex.ru/pogoda/ru/moscow',headers)

Temperature_Moscow = (pars_machine('https://www.foreca.com/ru/100524901/Moscow-Russia', headers, 'div','temp')[0].split())[0][:-1]
request('https://www.foreca.com/ru/100524901/Moscow-Russia',headers)

data_solar_wind = pars_machine('https://xras.ru/solar_wind.html', headers, 'div', 'graph_lastdata')
Solar_wind_density = (data_solar_wind[1].split())[0].strip()
Solar_wind_speed = (data_solar_wind[0].split())[0].strip()
Component_Bz = (data_solar_wind[-1].split())[0].strip()
request('https://xras.ru/solar_wind.html',headers)

data_diseases = pars_machine('https://www.influenza.spb.ru/surveillance/flu-bulletin/', headers, 'td', 'repTblCell')
Number_of_people_tested_for_influenza = int(data_diseases[5])
Number_of_people_infected_with_influenza = int(data_diseases[20])
Number_of_people_tested_for_ARVI = int(data_diseases[24])
Number_of_people_infected_with_ARVI = int(data_diseases[48])
Number_of_people_tested_for_COVID19 = int(data_diseases[52])
Number_of_people_infected_with_COVID19 = int(data_diseases[55])
request('https://www.influenza.spb.ru/surveillance/flu-bulletin/',headers)

Magnetic_storm_forecast = magnetic_storm_forecasts(Solar_wind_speed, Solar_wind_density, Component_Bz)

data_weather = {
    'Indicators': [
        'Date:',
        'Temperature (Celsius):',
        'Wind speed (km/h):',
        'Humidity (%):',
        'Absolute Humidity (g/m³):',
        'Atmosphere pressure (mmHg):',
        'Ultraviolet index:',
        'Current air quality (AQI):',
        'Nitrogen dioxide (NO2, µg/m³):',
        'Sulfur dioxide (SO2, µg/m³):',
        'Ozone (O3, µg/m³):',
        'Carbon dioxide (CO, µg/m³):',
        'Large particles (PM10, µg/m³):',
        'Small particles (PM2.5, µg/m³):',
        'Magnetic storms (Kp):',
        'Pollen (state):',
        'Solar wind speed (km/s):',
        'Solar wind density (cm³):',
        'Component Bz (nT):',
        'Tested for influenza (units):',
        'Infected with influenza (units):',
        'Tested for ARVI (units):',
        'Infected with ARVI (units):',
        'Tested for COVID19 (units):',
        'Infected with COVID19 (units):',
        'Magnetic storm hazard level:'
    ],
    'Saint_Petersburg': [
        datetime.datetime.now().replace(microsecond=0),
        Temperature_Saint_Petersburg,
        wind_speed_Saint_Petersburg,
        Humidity_index_Saint_Petersburg,
        absolute_humidity_arden_bakk(Humidity_index_Saint_Petersburg, Temperature_Saint_Petersburg),
        Atm_pressure_Saint_Petersburg,
        UV_index_Saint_Petersburg,
        Current_air_quality_Saint_Petersburg,
        data_pollution_Saint_Petersburg[0],
        data_pollution_Saint_Petersburg[2],
        data_pollution_Saint_Petersburg[3],
        data_pollution_Saint_Petersburg[5],
        data_pollution_Saint_Petersburg[1],
        data_pollution_Saint_Petersburg[4],
        Magnetic_storms_Saint_Petersburg,
        data_pollen_Saint_Petersburg[0],
        Solar_wind_speed,
        Solar_wind_density,
        Component_Bz,
        Number_of_people_tested_for_influenza,
        Number_of_people_infected_with_influenza,
        Number_of_people_tested_for_ARVI,
        Number_of_people_infected_with_ARVI,
        Number_of_people_tested_for_COVID19,
        Number_of_people_infected_with_COVID19,
        Magnetic_storm_forecast
    ],
    'Moscow': [
        datetime.datetime.now().replace(microsecond=0),
        Temperature_Moscow,
        wind_speed_Moscow,
        Humidity_index_Moscow,
        absolute_humidity_arden_bakk(Humidity_index_Moscow, Temperature_Moscow),
        Atm_pressure_Moscow,
        UV_index_Moscow,
        Current_air_quality_Moscow,
        data_pollution_Moscow[0],
        data_pollution_Moscow[2],
        data_pollution_Moscow[3],
        data_pollution_Moscow[5],
        data_pollution_Moscow[1],
        data_pollution_Moscow[4],
        Magnetic_storms_Moscow,
        data_pollen_Moscow[0],
        Solar_wind_speed,
        Solar_wind_density,
        Component_Bz,
        Number_of_people_tested_for_influenza,
        Number_of_people_infected_with_influenza,
        Number_of_people_tested_for_ARVI,
        Number_of_people_infected_with_ARVI,
        Number_of_people_tested_for_COVID19,
        Number_of_people_infected_with_COVID19,
        Magnetic_storm_forecast
    ]
}

df_weather = DataFrame(data_weather)
print(df_weather)

df_weather = df_weather.set_index('Indicators')
spb_data = df_weather['Saint_Petersburg']
mos_data = df_weather['Moscow']
indicator_to_column = {
    'Date:': 'date',
    'Temperature (Celsius):': 'temperature',
    'Wind speed (km/h):': 'wind_speed',
    'Humidity (%):': 'humidity',
    'Absolute Humidity (g/m³):': 'absolute_humidity',
    'Atmosphere pressure (mmHg):': 'atmosphere_pressure',
    'Ultraviolet index:': 'uv',
    'Current air quality (AQI):': 'aqi',
    'Nitrogen dioxide (NO2, µg/m³):': 'no2',
    'Sulfur dioxide (SO2, µg/m³):': 'so2',
    'Ozone (O3, µg/m³):': 'o3',
    'Carbon dioxide (CO, µg/m³):': 'co',
    'Large particles (PM10, µg/m³):': 'pm10',
    'Small particles (PM2.5, µg/m³):': 'pm2_5',
    'Magnetic storms (Kp):': 'magnetic_storms',
    'Pollen (state):': 'pollen',
    'Solar wind speed (km/s):': 'solar_w_speed',
    'Solar wind density (cm³):': 'solar_w_density',
    'Component Bz (nT):': 'bz',
    'Tested for influenza (units):': 'tested_influenza',
    'Infected with influenza (units):': 'inf_influenza',
    'Tested for ARVI (units):': 'tested_arvi',
    'Infected with ARVI (units):': 'inf_arvi',
    'Tested for COVID19 (units):': 'tested_covid19',
    'Infected with COVID19 (units):': 'inf_covid19',
    'Magnetic storm hazard level:': 'magnetic_hazard'
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
        COPY data_weather_saint_petersburg ({columns}) 
        FROM STDIN WITH CSV
        """,
        file=sio_spb
    )
    connection.commit()

with connection.cursor() as co:
    columns = ', '.join(df_for_db2.columns.tolist())
    co.copy_expert(
        sql=f"""
        COPY data_weather_moscow ({columns}) 
        FROM STDIN WITH CSV
        """,
        file=sio_moscow
    )
    connection.commit()
connection.close()