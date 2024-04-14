import logging
from math import cos, sin, asin, sqrt, radians, log

import database
from config import TOKEN_STATIC
from translation import lang_code, t

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('GEOGESSER')

async def get_url(cords):
    lat1, lon1, _, lat2, lon2 = map(float, cords.split())
    return f"https://static-maps.yandex.ru/v1?pl=c:8822DDC0,w:3,{lon1},{lat1},{lon2},{lat2}&pt={lon1},{lat1},flag~{lon2},{lat2},comma&apikey={TOKEN_STATIC}"

async def calculate_score_and_distance(cords):
    lat1, lon1, _, lat2, lon2 = map(float, cords.split())

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    metres = 6371 * c * 1000
    score = max(min(-log(metres / 70, 1.0014) + 5000, 5000), 0)
    return [int(score), int(metres)]

async def calculate_score_and_distance_moscow_spb(cords):
    lat1, lon1, _, lat2, lon2 = map(float, cords.split())

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    metres = 6371 * c * 1000
    score = max(min(5000-log((metres + 90)/ 100, 1.001), 5000), 0)
    return [int(score), int(metres)]

async def calculate_score_and_distance_russia(cords):
    lat1, lon1, _, lat2, lon2 = map(float, cords.split())

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    metres = 6371 * c * 1000
    score = max(min(5000-log((metres + 2900)/ 3000, 1.00141), 5000), 0)
    return [int(score), int(metres)]

async def create_result_text(score, metres, lang = 'en'):
    txt = ""
    if metres < 10000:
        txt = (t['score and meters'][lang_code[lang]]).format(score, metres)
    elif metres < 100000:
        txt = (t['score and kilometers'][lang_code[lang]]).format(score, round(metres / 1000, 2))
    else:
        txt = (t['score and kilometers'][lang_code[lang]]).format(score, round(metres / 1000, 0))

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
        txt += (t['top 10'][lang_code[lang]]).format(i + 1, top_10_users[i]["username"], top_10_users[i][mode.lower() +"_single_mean_score"],
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
        txt += (t['last 5 res'][lang_code[lang]]).format(i + 1, games[i][0], games[i][1])
    if len(games) == 0:
        txt = (t['no games'][lang_code[lang]])
    return txt