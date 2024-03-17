import aiohttp
from config import get_settings
from datetime import datetime
from config import get_constants
settings = get_settings()


class TomTomAPI:
    async def get_route(self, lan1: float, log1: float, lan2: float, log2: float, transport_type: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://api.tomtom.com/routing/1/calculateRoute/{log1},{lan1}:{log2},{lan2}/json?key={settings.TOM_TOM_APIKEY}&travelMode={transport_type}&routeType=fastest") as response:
                json = await response.json()
                try:
                    return json["routes"][0]["legs"][0]["points"]
                except KeyError:
                    return "No route"

d = datetime.strptime("1/1/2023 5:21",get_constants().TIME_PATTERN)
print(d.time()<datetime.strptime("6:00","%H:%M").time())