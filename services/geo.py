from typing import Optional

from geopy.geocoders import ArcGIS
from geopy.adapters import AioHTTPAdapter
from geopy.distance import geodesic
from geopy import Location


class GeoPyAPI:
    async def get_coordinates(self, node_text: str) -> Optional[tuple]:
        """lat,lon"""
        async with ArcGIS(user_agent="GetLoc", adapter_factory=AioHTTPAdapter, timeout=10) as locator:
            location = await locator.geocode(node_text, exactly_one=True)
            if location is None:
                return None
            return round(location.latitude, 2), round(location.longitude, 2)

    async def get_geocode(self, node_lat: float, node_lon: float) -> Optional[Location]:
        async with ArcGIS(user_agent="GetLoc", adapter_factory=AioHTTPAdapter, timeout=10) as locator:
            location = await locator.reverse((node_lat, node_lon))
            if location is None:
                return None
            return location

    async def get_distance(self, coordinates_1: tuple, coordinates_2: tuple) -> int:
        return geodesic(coordinates_1, coordinates_2).km
