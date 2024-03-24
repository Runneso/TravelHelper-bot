import aiohttp
from config import get_settings, Settings

settings: Settings = get_settings()


class Place:
    def __init__(self, name: str, address: str, phone_number: str, url: str, opening_hours: str):
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.url = url
        self.opening_hours = opening_hours

    def __repr__(self):
        return repr({"name": self.name,
                     "address": self.address,
                     "phone_number": self.phone_number,
                     "url": self.url,
                     "opening_hours": self.opening_hours})


class TomTomAPI:
    async def get_route(self, lat1: float, lon1: float, lat2: float, lon2: float, transport_type: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://api.tomtom.com/routing/1/calculateRoute/{lat1},{lon1}:{lat2},{lon2}/json?key={settings.TOM_TOM_APIKEY.get_secret_value()}&travelMode={transport_type}&routeType=fastest") as response:
                json = await response.json()
                try:
                    return json["routes"][0]["legs"][0]["points"]
                except KeyError:
                    return None

    async def get_poi_catalog(self):
        with open("poi.txt", "w", encoding="utf-8") as file:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        f"https://api.tomtom.com/search/2/poiCategories.json?key={settings.TOM_TOM_APIKEY.get_secret_value()}") as response:
                    json = await response.json()
                    for item in json["poiCategories"]:
                        file.write(f"{item['id']} {item['name']}\n")

    async def get_around(self, type_of_place: list[int], lat: float, lon: float):
        api_url = f"https://api.tomtom.com/search/2/poiSearch/.json?key={settings.TOM_TOM_APIKEY.get_secret_value()}&lat={lat}&lon={lon}&radius=10000&language=ru-RU&limit=15"
        for tag in type_of_place:
            api_url += f"&categorySet={tag}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                json = await response.json()
                array = list()
                for place in json["results"]:
                    name = place['poi']['name']
                    try:
                        phone_number = place['poi']['phone']
                    except KeyError:
                        phone_number = "ОТСУСТВУЕТ"
                    try:
                        url = place['poi']['url']
                    except KeyError:
                        url = "ОТСУСТВУЕТ"
                    try:
                        opening_hours = place['poi']['opening_hours']
                    except KeyError:
                        opening_hours = "ОТСУСТВУЕТ"
                    address = (place["address"]['freeformAddress'])
                    array.append(Place(name, address, phone_number, url, opening_hours))
                return array

    async def get_attractions(self, lat: float, lon: float):
        places = await self.get_around([7376, 7318, 7317, 9302, 9932, 9927], lat, lon)
        return places

    async def get_restaurants(self, lat: float, lon: float):
        places = await self.get_around(
            [7315, 9376, 7315081, 7315002, 7315082, 7315003, 7315083, 7315084, 7315085, 7315087, 7315086, 7315004,
             7315088, 7315146, 9379004, 7315006, 7315007, 7315089, 7315008, 7315142, 7315009, 7315090, 7315009, 7315010,
             7315070, 7315093, 7315012], lat, lon)
        return places

    async def get_hotels(self, lat: float, lon: float):
        places = await self.get_around(
            [7314], lat, lon)
        return places
