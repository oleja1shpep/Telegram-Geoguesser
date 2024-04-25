import logging
import os
import g4f
import json
import numpy as np
import requests

from math import cos, sin, asin, sqrt, radians, log
from dotenv import load_dotenv
from geopy.distance import geodesic

from backend.database import MongoDB

database = MongoDB()

load_dotenv()

TOKEN_STATIC = os.getenv("TOKEN_STATIC")

with open('./backend/text/translations.json', 'r', encoding='utf-8') as file:
    file = json.load(file)
translation = file['translations']
lang_code = file['lang_code']


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('GEOGESSER')
logger.setLevel(logging.DEBUG)

async def gpt_request(cords, language):
    lat1, lon1, lat2, lon2 = map(str, cords.split())
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat1}&lon={lon1}"
    response = requests.get(url)
    address = ''
    if response.status_code == 200:
        data = response.json()
        address = data.get('display_name')
        logger.info("In function: gpt_request: Got address")
    else:
        logger.warning("In function: gpt_request: Coords request error")

    request = f"give me some fan fact about {address} using {language} language. Message text should be no longer that 50 words"

    answer = await g4f.ChatCompletion.create_async(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": request}])
    return answer

async def get_url(cords):
    lat1, lon1, lat2, lon2 = map(float, cords.split())
    return f"https://maps.googleapis.com/maps/api/staticmap?path=color:0x0000ff80|weight:5|{lat1},{lon1}|
       {lat2},{lon2}&markers=icon:https://storage.yandexcloud.net/test-geoguessr/correct_marker.png|{lat1},{lon1}&
       markers=icon:https://storage.yandexcloud.net/test-geoguessr/marker.png|{lat2},{lon2}|&size=600x600&key=AIzaSyB90M6YMN89duMBupapc6x7_K8gRNGw7sk"

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

async def create_result_text(score, metres, seed, lang = 'en'):
    txt = ""
    if metres < 10000:
        txt = (translation['score and meters'][lang_code[lang]]).format(score, metres)
    elif metres < 100000:
        txt = (translation['score and kilometers'][lang_code[lang]]).format(score, round(metres / 1000, 2))
    else:
        txt = (translation['score and kilometers'][lang_code[lang]]).format(score, round(metres / 1000, 0))
    txt += f"\nSeed: `{seed}`"
    return txt

async def get_top10_single(mode, lang = 'en'):
    try:
        top_10_users = database.get_top10_single(mode)
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
        games = database.get_last5_results(tele_id, mode)
        logger.info("connected to db. got last 5 games in signle " + mode)
    except Exception as e:
        logger.error(e)

    txt = ''
    for i in range(len(games)):
        metres = games[i][1]
        if metres < 10000:
            txt += (translation['last 5 res metres'][lang_code[lang]]).format(i + 1, games[i][0], metres)
        elif metres < 100000:
            txt += (translation['last 5 res km'][lang_code[lang]]).format(i + 1, games[i][0], round(metres / 1000, 2))
        else:
            txt += (translation['last 5 res km'][lang_code[lang]]).format(i + 1, games[i][0], round(metres / 1000, 0))

    if len(games) == 0:
        txt = (translation['no games'][lang_code[lang]])
    return txt
