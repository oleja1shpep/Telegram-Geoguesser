import numpy as np
from geopy.distance import geodesic
from database import add_user, find_user, set_language, get_language
from backend.bot_functions import calculate_score_and_distance_moscow_spb, calculate_score_and_distance_russia, calculate_score_and_distance_world
import asyncio
import inspect

def asyncio_run(async_func):
    def wrapper(*args, **kwargs):
        return asyncio.run(async_func(*args, **kwargs))

    wrapper.__signature__ = inspect.signature(async_func)  # without this, fixtures are not injected

    return wrapper


@asyncio_run
async def test_calculate_score_and_distance_moscow_spb_1():
    coord = "55.570334 37.328205 55.678887 37.484074"
    result = await calculate_score_and_distance_moscow_spb((coord))
    assert result == [245, 15571]

@asyncio_run
async def test_calculate_score_and_distance_moscow_spb_2():
    coord = "60.180033 30.613642 59.900224 30.336237"
    result = await calculate_score_and_distance_moscow_spb((coord))
    assert result == [195, 34797]

@asyncio_run
async def test_calculate_score_and_distance_russia():
    coord = "55.798913 49.035561 60.168747 44.460636"
    result = await calculate_score_and_distance_russia((coord))
    print(result)
    assert result == [3120, 556589]

@asyncio_run
async def test_calculate_score_and_distance_world():
    coord = "51.784990 10.096771 49.785721 15.368280"
    result = await calculate_score_and_distance_world((coord))
    print(result)
    assert result == [3623, 433046]

@asyncio_run
async def test_add_user_1():
    await add_user('abra', 'cadabra')
    res = await find_user('abra', 'cadabra')
    assert res == True


@asyncio_run
async def test_add_user_2():
    res = await find_user('abra_2', 'cadabra_2')
    assert res == False

@asyncio_run
async def test_set_language():
    await add_user('a', 'b')
    await set_language('a', 'rus')
    res = await get_language('a')
    assert res == 'rus'