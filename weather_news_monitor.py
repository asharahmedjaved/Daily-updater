import requests
import schedule
import time
import smtplib
from datetime import datetime
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env.local
load_dotenv('.env.local')

# Constants loaded from .env.local
CITY = os.getenv("CITY")
COUNTRY = os.getenv("COUNTRY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ASTRONOMY_APP_ID = os.getenv("ASTRONOMY_APP_ID")
ASTRONOMY_APP_SECRET = os.getenv("ASTRONOMY_APP_SECRET")
NASA_API_KEY = os.getenv("NASA_API_KEY")
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# URLs
FORECAST_URL = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
NEWS_URL = f"https://newsapi.org/v2/top-headlines?country={COUNTRY}&apiKey={NEWS_API_KEY}"
AIR_QUALITY_URL = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={{lat}}&lon={{lon}}&appid={WEATHER_API_KEY}"
ASTRONOMY_TOKEN_URL = "https://api.astronomyapi.com/oauth/token"
ASTRONOMY_MOON_PHASE_URL = f"https://api.astronomyapi.com/v2/bodies/positions/moon?latitude={{lat}}&longitude={{lon}}&elevation=0"
NASA_EVENTS_URL = f"https://api.nasa.gov/DONKI/FLR?startDate={datetime.now().strftime('%Y-%m-%d')}&api_key={NASA_API_KEY}"


def send_email(subject, body):
    # Create a MIMEText object with UTF-8 encoding
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def log_report(report):
    with open("weather_news_report.log", "a") as file:
        file.write(report + "\n\n")

def get_weather():
    try:
        response = requests.get(WEATHER_URL)
        data = response.json()
        
        if data["cod"] != 200:
            print(f"Error fetching weather data: {data.get('message', 'Unknown error')}")
            return None

        temp = data['main']['temp']
        weather_desc = data['weather'][0]['description']
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        return temp, weather_desc, lat, lon
    except Exception as e:
        print(f"Exception occurred in get_weather: {e}")
        return None

def get_hourly_weather():
    response = requests.get(FORECAST_URL)
    data = response.json()
    
    if data["cod"] != "200":
        print("Error fetching forecast data")
        return None
    
    forecast_list = data['list']  # List of 3-hour interval forecasts
    hourly_forecast = []

    for entry in forecast_list:
        timestamp = entry['dt']
        time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        temp = entry['main']['temp']
        weather_desc = entry['weather'][0]['description']
        hourly_forecast.append(f"{time}: {weather_desc} at {temp}°C")
    
    return hourly_forecast

def get_air_quality(lat, lon):
    response = requests.get(AIR_QUALITY_URL.format(lat=lat, lon=lon))
    data = response.json()
    
    if "list" not in data:
        print("Error fetching air quality data")
        return None
    
    aqi = data["list"][0]["main"]["aqi"]
    return aqi

def get_clothing_recommendation(temp, aqi):
    clothing = ""
    
    if temp >= 25:
        clothing = "It's warm! Wear light and breathable clothes."
    elif 15 <= temp < 25:
        clothing = "It's a bit chilly. A light jacket should suffice."
    elif 5 <= temp < 15:
        clothing = "It's cold. Wear a warm jacket or sweater."
    else:
        clothing = "It's freezing! Wear heavy winter clothing, including gloves and a hat."

    if aqi:
        if aqi > 3:
            clothing += " The air quality is poor, consider wearing a mask if going outside."

    return clothing

# def get_astronomy_api_token():
#     """Get the OAuth token from AstronomyAPI."""
    
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded"  # Ensure this content type
#     }
    
#     data = {
#         "grant_type": "client_credentials",
#         "client_id": ASTRONOMY_APP_ID,
#         "client_secret": ASTRONOMY_APP_SECRET
#     }
    
#     try:
#         response = requests.post(ASTRONOMY_TOKEN_URL, data=data, headers=headers)
        
#         if response.status_code != 200:
#             print(f"Error getting token: {response.status_code}, {response.text}")
#             return None

#         token_data = response.json()
#         return token_data['access_token']
    
#     except Exception as e:
#         print(f"Exception occurred: {e}")
#         return None


# def get_moon_phase(token, lat, lon):
#     headers = {
#         "Authorization": f"Bearer {token}"
#     }
#     response = requests.get(ASTRONOMY_MOON_PHASE_URL.format(lat=lat, lon=lon), headers=headers)
    
#     data = response.json()
    
#     if 'data' not in data:
#         print("Error fetching moon phase data")
#         return None
    
#     moon_phase = data['data']['table']['rows'][0]['cells'][0]['extraInfo']['moonPhase']['phase']
#     return moon_phase###

def get_nasa_events():
    response = requests.get(NASA_EVENTS_URL)
    data = response.json()
    
    if not data:
        print("Error fetching NASA events data")
        return None
    
    events = []
    for event in data:
        title = event.get("classType", "Unknown Event")
        start_time = event.get("beginTime", "Unknown Time")
        events.append(f"{title} - Starts at {start_time}")
    
    return events

def get_news():
    response = requests.get(NEWS_URL)
    data = response.json()
    
    if data["status"] != "ok":
        print("Error fetching news data")
        return None
    
    headlines = [article['title'] for article in data['articles'][:5]]
    return headlines

def report():
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_content = f"Report generated at {report_time}\n\n"
    
    # Get weather information
    weather = get_weather()
    if weather:
        temp, description, lat, lon = weather
        air_quality = get_air_quality(lat, lon)
        clothing = get_clothing_recommendation(temp, air_quality)
        report_content += f"Weather in {CITY}: {description} at {temp}°C.\n"
    else:
        report_content += "Weather information unavailable.\n\n"

    hourly_weather = get_hourly_weather()
    if hourly_weather:
        report_content += f"Hourly weather forecast for {CITY}:\n"
        for forecast in hourly_weather:
            report_content += f"{forecast}\n"
        if air_quality:
            report_content += f"Air Quality Index (AQI): {air_quality}\n"
        
    else:
        report_content += "Hourly weather forecast unavailable.\n\n"

    # # Get AstronomyAPI OAuth token
    # token = get_astronomy_api_token()
    # if not token:
    #     print("Failed to retrieve Astronomy API token. Aborting report generation.")
        

    # # Get moon phase
    # moon_phase = get_moon_phase(token, lat, lon)
    # if moon_phase:
    #     report_content += f"Moon Phase: {moon_phase}\n"
    # else:
    #     report_content += "Moon phase information unavailable.\n"

    # Get NASA events
    nasa_events = get_nasa_events()
    if nasa_events:
        report_content += "\nUpcoming Astronomical Events:\n"
        for event in nasa_events:
            report_content += f"- {event}\n"
    else:
        report_content += "No upcoming astronomical events available.\n"
    
    # Get news headlines
    news = get_news()
    if news:
        report_content += "Today's Top Headlines:\n"
        for i, headline in enumerate(news, 1):
            report_content += f"{i}. {headline}\n"
    else:
        report_content += "News information unavailable.\n"

    # Log the report
    log_report(report_content)
    
    # Send email notification
    send_email(f"Daily Report - {CITY}", report_content)

    print(report_content)

# Schedule the report to run every morning at 7 AM
schedule.every().day.at("07:00").do(report)

# Running the schedule
if __name__ == "__main__":
    print(f"Starting weather and news monitor for {CITY}...")

    # Run an initial report
    report()

    # Run the scheduled reports
    while True:
        schedule.run_pending()
        time.sleep(60)  # Wait one minute before checking again
