import requests
import pandas as pd
import schedule
import time
from datetime import datetime
import matplotlib.pyplot as plt

API_KEY = 'cd58477dbd91f859801bf5e1f264f9fa'
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def fetch_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = kelvin_to_celsius(data['main']['temp'])
        feels_like = kelvin_to_celsius(data['main']['feels_like'])
        weather = data['weather'][0]['main']
        timestamp = datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
        return {'city': city, 'temp': temp, 'feels_like': feels_like, 'weather': weather, 'timestamp': timestamp}
    else:
        print(f"Failed to fetch weather data for {city}")
        return None
    
def log_weather():
    weather_data = []
    for city in CITIES:
        data = fetch_weather(city)
        if data:
            weather_data.append(data)
    df = pd.DataFrame(weather_data)
    print(df)
    df.to_csv('weather_data.csv', mode='a', header=False, index=False)
    
ALERT_THRESHOLD = 35 #example threshold in celsius

def check_threshold():
    try:
        df = pd.read_csv('weather_data.csv', names=['city', 'temp', 'feels_like', 'weather', 'timestamp'])
        for _, row in df.iterrows():
            if row['temp'] > ALERT_THRESHOLD:
                print(f"Alert! Temperature in {row['city']} exceeded {ALERT_THRESHOLD}C at {row['timestamp']}.")
    except FileNotFoundError:
        print("No weather data available yet. Waiting for the first log entry.")
        
def plot_weather():
    try:
        df = pd.read_csv('weather_data.csv', names=['city', 'temp', 'feels_like', 'weather', 'timestamp'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        plt.figure(figsize=(10, 6))
        for city in CITIES:
            city_data = df[df['city'] == city]
            plt.plot(city_data['timestamp'], city_data['temp'], label=city)
        
        plt.xlabel('Time')
        plt.ylabel('Temperature (C)')
        plt.title('Temperature Trends')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
    except FileNotFoundError:
        print("No weather data available yet to plot.")
        
schedule.every(5).minutes.do(log_weather)
schedule.every(5).minutes.do(check_threshold)
schedule.every().day.at("18:00").do(plot_weather)

if __name__ == '__main__':
    print("Starting weather monitoring....")
    while True:
        schedule.run_pending()
        time.sleep(1)