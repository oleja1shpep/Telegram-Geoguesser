import logging
import os
import asyncio
import g4f
import json
import numpy as np

from asyncio import WindowsSelectorEventLoopPolicy
from math import cos, sin, asin, sqrt, radians, log
from dotenv import load_dotenv
from geopy.distance import geodesic

from translation import lang_code, t

import database

load_dotenv()

TOKEN_STATIC = os.getenv("TOKEN_STATIC")

with open('translations.json', 'r', encoding='utf-8') as file:
    file = json.load(file)
translation = file['translations']
lang_code = file['lang_code']


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('GEOGESSER')
logger.setLevel(logging.DEBUG)

async def get_url(cords):
    lat1, lon1, lat2, lon2 = map(float, cords.split())
    return f"https://static-maps.yandex.ru/v1?pl=c:8822DDC0,w:3,{lon1},{lat1},{lon2},{lat2}&pt={lon1},{lat1},flag~{lon2},{lat2},comma&apikey={TOKEN_STATIC}"

async def calculate_score_and_distance(cords):
    lat1, lon1, lat2, lon2 = map(float, cords.split())

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    metres = 6371 * c * 1000
    score = max(min(-log(metres / 70, 1.0014) + 5000, 5000), 0)
    return [int(score), int(metres)]

async def calculate_score_and_distance_moscow_spb(cords):
    lat1, lon1, lat2, lon2 = map(float, cords.split())
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    distance = geodesic(point1, point2).meters
    square = 2651
    scale = 1.99606121e-19 * square + 3.41291449e-12 * square + 5.83462311e-05 * square + 6.85055291e+00 * square
    score = min(5000, int(np.exp(7.02299068e-13*distance**3 - 2.00281581e-08*distance**2 -2.14312600e-04*distance + 8.44295074e+00)))
    if (distance < 10):
        score = 5000
    return [score, int(distance)]

async def calculate_score_and_distance_russia(cords):
    lat1, lon1, lat2, lon2 = map(float, cords.split())
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    distance = geodesic(point1, point2).meters
    score = min(5000, int(np.exp(8.92179927e-21*distance**3 - 1.08930162e-13*distance**2 - 5.00975103e-07*distance +
    8.44085571e+00)))
    if (distance < 100):
        score = 5000
    return [int(score), int(distance)]

async def create_result_text(score, metres,  message, lang = 'en',):
    txt = ""
    if metres < 10000:
        txt = (translation['score and meters'][lang_code[lang]]).format(score, metres)
    elif metres < 100000:
        txt = (translation['score and kilometers'][lang_code[lang]]).format(score, round(metres / 1000, 2))
    else:
        txt = (translation['score and kilometers'][lang_code[lang]]).format(score, round(metres / 1000, 0))
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    response = await g4f.ChatCompletion.create_async(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}])
    txt += "\n" + response
    return txt

async def get_top10_single(mode, lang = 'en'):
    try:
        top_10_users = await database.get_top10_single(mode)
        logger.info("connected to db. got top 10 players in signle " + mode)
    except Exception as e:
        logger.error(e)
    txt = ''
    # print("- - - - - - - ")
    # print(top_10_users)
    # print("- - - - - - - ")
    for i in range(len(top_10_users)):
        txt += (translation['top 10'][lang_code[lang]]).format(i + 1, top_10_users[i]["username"], top_10_users[i][mode.lower() +"_single_mean_score"],
                                                              top_10_users[i][mode.lower() +"_single_game_counter"])
    # print(top_10_users)
    return txt

async def get_last5_results_single(tele_id, mode, lang = 'en'):
    try:
        games = await database.get_last5_results(tele_id, mode)
        logger.info("connected to db. got last 5 games in signle " + mode)
    except Exception as e:
        logger.error(e)

    txt = ''
    for i in range(len(games)):
        txt += (translation['last 5 res'][lang_code[lang]]).format(i + 1, games[i][0], games[i][1])
    if len(games) == 0:
        txt = (translation['no games'][lang_code[lang]])
    return txt