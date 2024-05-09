import numpy as np
from geopy.distance import geodesic

# from backend.bot_functions import calculate_score_and_distance_moscow_spb
import asyncio
import inspect

async def calculate_score_and_distance_moscow_spb(cords):
    lat1, lon1, lat2, lon2 = map(float, cords.split())
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    distance = geodesic(point1, point2).meters
    square = 2651
    scale = 1.99606121e-19 * square + 3.41291449e-12 * square + 5.83462311e-05 * square + 6.85055291e+00 * square
    score = min(5000, int(np.exp(-3.05857510e-04 * distance + 8.47977747e+00)+ 198.33077405051245))
    if (distance < 10):
        score = 5000
    return [score, int(distance)]

async def calculate_score_and_distance_russia(cords):
    lat1, lon1, lat2, lon2 = map(float, cords.split())
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    distance = geodesic(point1, point2).meters
    score = min(5000, int(np.exp(-7.13667523e-07*distance +  8.47673317e+00) + 198.33077405052063))
    if (distance < 100):
        score = 5000
    return [int(score), int(distance)]

async def calculate_score_and_distance_world(cords):
    lat1, lon1, lat2, lon2 = map(float, cords.split())
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    distance = geodesic(point1, point2).meters
    score = min(5000, int(np.exp(-5.35250642e-07*distance +  8.47672960e+00) + 198.33077405050426))
    if (distance < 100):
        score = 5000
    return [int(score), int(distance)]

def asyncio_run(async_func):
    def wrapper(*args, **kwargs):
        return asyncio.run(async_func(*args, **kwargs))

    wrapper.__signature__ = inspect.signature(async_func)  # without this, fixtures are not injected

    return wrapper


@asyncio_run
async def test_msk():
    coord = "55.570334 37.328205 55.678887 37.484074"
    result = await calculate_score_and_distance_moscow_spb((coord))
    assert result == [239, 15571]

@asyncio_run
async def test_sbp():
    coord = "60.180033 30.613642 59.900224 30.336237"
    result = await calculate_score_and_distance_moscow_spb((coord))
    assert result == [198, 34797]

@asyncio_run
async def test_rus():
    coord = "55.798913 49.035561 60.168747 44.460636"
    result = await calculate_score_and_distance_russia((coord))
    print(result)
    assert result == [3425, 556589]

@asyncio_run
async def test_world():
    coord = "51.784990 10.096771 49.785721 15.368280"
    result = await calculate_score_and_distance_world((coord))
    print(result)
    assert result == [4006, 433046]