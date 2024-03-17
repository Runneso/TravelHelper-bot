import aiohttp
from config import get_settings
from datetime import datetime

settings = get_settings()


class OpenWeatherAPI:
    async def get_forecast(self, lat: float, lon: float):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={settings.OPEN_WEATHER_APIKEY}&lang=ru&cnt=100&units=metric") as response:
                json = await response.json()
                result = list()
                try:
                    for item in json["list"]:
                        result.append((datetime.fromtimestamp(item["dt"]), item["main"]["temp"]))
                    return result
                except KeyError:
                    return "No data"
