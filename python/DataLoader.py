import requests, os
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

# Retrieve forecast data from API
def get_weather_data(city):
    # Get API Key from .env file
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")

    # Get city coordinates from geopy library
    lat, lon = get_city_coordinates(city)

    # Set endpoint URL
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    # Get response from endpoint
    response = requests.get(url)
    data = response.json()

    if data["cod"] != "404":
        forecast = data["list"]
        return forecast
    else:
        return None

# Map city name to coordinates
def get_city_coordinates(city):
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="WeatherApp")
    location = geolocator.geocode(city)

    return location.latitude, location.longitude