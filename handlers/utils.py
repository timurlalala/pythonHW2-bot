from templates import SetProfileMessageTemplates
from typing import Dict, Any
import aiohttp
from config import OPEN_WEATHER_MAP_TOKEN

def generate_profile_summary(data: Dict[str, Any]):
    return SetProfileMessageTemplates.PROFILE_SUMMARY.format(**data)

async def acheck_city(city_name: str) -> bool:
    "Проверяет, есть ли название в базе OpenWeatherMap по API"
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=5&appid={OPEN_WEATHER_MAP_TOKEN}") as response:
            if response.status == 200:
                return True
            else:
                return False

async def get_city_temperature(city_name: str) -> float | None:
    "Получает температуру города по API OpenWeatherMap"
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPEN_WEATHER_MAP_TOKEN}") as response:
            if response.status == 200:
                data = await response.json()
                return data['main']['temp'] - 273.15  # Convert Kelvin to Celsius
            else:
                return None

async def get_food_info(food_name: str):
    """Ищет и возвращает информацию о продукте по API OpenFoodFacts"""
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={food_name}&json=true"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                products = data.get('products', [])
                if products:
                    return {
                        'food_name': products[0].get('product_name', 'Неизвестно'),
                        'norm_calories': products[0].get('nutriments', {}).get('energy-kcal_100g', 0)
                    }
                else:
                    return None
            else:
                print(f"Ошибка: {response.status}")
                return None

def calculate_burnt_calories(met: float, weight: float, minutes: int):
    """Рассчитывает количество сожженных калорий по MET, весу и времени в минутах."""
    calories_burnt = met * 3.5 * weight / 200 * minutes
    return round(calories_burnt, 2)

workout_met_mapping = {
    'бег': 8,
    'плавание': 6,
    'ходьба': 3,
    'приседания': 7.5,
    'подтягивания': 10
}