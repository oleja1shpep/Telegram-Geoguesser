import logging
import os
import json
import numpy as np
import requests
import matplotlib.pyplot as plt

from math import cos, sin, asin, sqrt, radians, log
from dotenv import load_dotenv
from geopy.distance import geodesic

from backend.database import MongoDB
from backend.text.links import STATIC_MAPS_LIGHT_LINK, STATIC_MAPS_DARK_LINK, YAGPT_LINK, GEOCODE_LINK
from backend.seed_processor import coordinates_and_landmark_from_seed_easy_mode

MODE_TO_GEOCODER_ARGS = {
    'msk': 'street_address|political',
    'spb': 'street_address|political',
    'rus': 'political', 
    'usa': 'political',
    'wrld': 'administrative_area_level_1|country',
    'easy': 'point_of_interest'
}

database = MongoDB()

load_dotenv()

TOKEN_STATIC = os.getenv("TOKEN_STATIC")
YAGPT_APIKEY = os.getenv("YAGPT_APIKEY")
GEOCODER_APIKEY = os.getenv("GEOCODER_APIKEY")
STATIC_MAPS_APIKEY = os.getenv("STATIC_MAPS_APIKEY")
FOLDER_ID = os.getenv("FOLDER_ID")

with open('./backend/text/translations.json', 'r', encoding='utf-8') as file:
    file = json.load(file)
translation = file['translations']
lang_code = file['lang_code']


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('GEOGESSER')
logger.setLevel(logging.DEBUG)

def form_payload(request):
    logger.debug(FOLDER_ID)
    payload = json.dumps({
    "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite/latest",
    "completionOptions": {
        "stream": False,
        "temperature": 0.2,
        "maxTokens": "2000"
    },
    "messages": [
        {
            "role": "system",
            "text": "Ты - экскурсовод, который отлично знает историю и географию. Текст не длиннее 50 слов."
        },
        {
            "role": "user",
            "text": request
        }
    ]
    })
    return payload

def get_address(lat, lon, mode, lang):
    response = requests.get(GEOCODE_LINK.format(lat, lon, MODE_TO_GEOCODER_ARGS[mode], lang, GEOCODER_APIKEY))
    code = response.status_code
    if code != 200:
        logger.warning(f"In function: get_address: Coords request error. Status code: {code}")
        return None
    data = response.json()
    addresses = data.get('results')
    if addresses == None:
        logger.info(f"In function: get_address: Incorrect response: no key 'results'")
        return None
    elif len(addresses) == 0:
        logger.info(f'In function: get_address: Zero results for {lat}, {lon}')
        return None
    
    address = addresses[0].get('formatted_address').split(', ')
    if mode == 'msk' or mode == 'spb':
        address = ', '.join([address[0]] + address[2:-1])
    elif mode == 'rus' or mode == 'usa':
        address = ', '.join(address[:-1])
    else:
        address = ', '.join(address)
    logger.info(f"In function: get_address: Got address: {address}")
    return address
        

def gpt_request(cords, seed, lang, mode):
    lat1, lon1, lat2, lon2 = map(str, cords.split())
    logger.debug(f"lat: {lat1}, lon: {lon1}")
    address = ''
    if mode == 'easy':
        x, y, landmark_id = coordinates_and_landmark_from_seed_easy_mode(seed)
        address = translation["landmarks"][lang_code[lang]][landmark_id]
    else:
        try:
            address = get_address(lat1, lon1, mode, lang)
        except Exception as e:
            logger.error(f"In function: gpt_request: {e}")
        if not address:
            if lang == "en":
                return f"Unable to come up with interesting fact"
            else:
                return f"Не удалось найти интересный факт"
    language = ''
    if lang == 'en':
        language = 'английском'
    else:
        language = "русском"
    if mode != 'easy':
        request = f"Напиши интересный факт на {language} языке об: {address}. Не упоминай сам адрес при ответе"
    else:
        request = f"Расскажи подробно о {address} на {language} языке"
    payload = form_payload(request)
    headers = {
        'Authorization': f'Api-Key {YAGPT_APIKEY}',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", YAGPT_LINK, headers=headers, data=payload)
    logger.debug(f"In function: gpt_request: response = {response.text}")
    try:
        if lang == 'en':
           text = f"Interesting fact about {address}:\n<blockquote>" + json.loads(response.text)["result"]["alternatives"][0]["message"]["text"] + "</blockquote>"
        else:
            text = f"Интересный факт про {address}:\n<blockquote>" + json.loads(response.text)["result"]["alternatives"][0]["message"]["text"] + "</blockquote>"
    except Exception as e:
        logger.error(f"In function: gpt_request: {e}")
        if lang == "en":
            return f"Unable to come up with interesting fact"
        else:
            return f"Не удалось найти интересный факт"

    return text

async def get_static_map_image(cords, colorScheme='light'):
    lat1, lon1, lat2, lon2 = map(float, cords.split())
    if colorScheme == 'light':
        return STATIC_MAPS_LIGHT_LINK.format(lat1, lon1, lat2, lon2, lat1, lon1, lat2, lon2, STATIC_MAPS_APIKEY)
    return STATIC_MAPS_DARK_LINK.format(lat1, lon1, lat2, lon2, lat1, lon1, lat2, lon2, STATIC_MAPS_APIKEY)

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
    score = min(5000, int(182.08274202255325 + (1 / (-1.57363469e-19 * distance**4 + 7.96561566e-15 * distance**3  - 2.97318716e-11*distance**2 + 1.28018881e-07*distance + 2.06281343e-04))))
    return [score, int(distance)]

async def calculate_score_and_distance_russia(cords):
    lat1, lon1, lat2, lon2 = map(float, cords.split())
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    distance = geodesic(point1, point2).meters
    score = min(5000, int(182.08274326504306 + (1 / (-4.66456406e-30 * distance**4 + 1.01113230e-22* distance**3 - 1.60579053e-16* distance**2 + 2.97335232e-10 * distance + 2.07552620e-04))))
    return [int(score), int(distance)]

async def calculate_score_and_distance_world(cords):
    lat1, lon1, lat2, lon2 = map(float, cords.split())
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    distance = geodesic(point1, point2).meters
    score = min(5000, int(182.08275087546463 + (1 / (-1.47589722e-30* distance**4 +  4.26571047e-23* distance**3 - 9.03248644e-17* distance**2 + 2.23000220e-10* distance  + 2.07554107e-04))))
    return [int(score), int(distance)]

async def create_result_text(score, metres, seed, lang = 'en'):
    txt = ""
    if metres < 10000:
        txt = (translation['score and meters'][lang_code[lang]]).format(score, metres)
    elif metres < 100000:
        txt = (translation['score and kilometers'][lang_code[lang]]).format(score, round(metres / 1000, 1))
    else:
        txt = (translation['score and kilometers'][lang_code[lang]]).format(score, int(round(metres / 1000, 0)))
    txt += f"\nSeed: `{seed}`"
    return txt

async def get_top10_single(tele_id, mode, lang = 'en'):
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
    find_user = database.users.find_one({"tele_id" : tele_id})
    txt += '\n...............................................\n'
    txt += (translation['top 10'][lang_code[lang]]).format('#', find_user["username"], find_user[mode.lower() +"_single_mean_score"],
                                                              find_user[mode.lower() +"_single_game_counter"])
    
    if (find_user[mode.lower() +"_single_game_counter"] < 5):
        txt += "\n" + translation["less than 5 games"][lang_code[lang]]
    return txt

async def get_last5_results_single(tele_id, mode, lang = 'en'):
    try:
        games = database.get_last_results(tele_id, mode)
        logger.info("connected to db. got last 5 games in single " + mode)
    except Exception as e:
        logger.error(e)

    txt = ''
    for i in range(len(games) - 1, max(-1, len(games) - 6), -1):
        metres = games[i][1]
        if metres < 10000:
            txt += (translation['last 5 res metres'][lang_code[lang]]).format(i + 1, games[i][0], metres)
        elif metres < 100000:
            txt += (translation['last 5 res km'][lang_code[lang]]).format(i + 1, games[i][0], round(metres / 1000, 1))
        else:
            txt += (translation['last 5 res km'][lang_code[lang]]).format(i + 1, games[i][0], int(round(metres / 1000, 0)))

    if len(games) == 0:
        txt = (translation['no games'][lang_code[lang]])
    return txt


async def form_statistics_graph(tele_id, mode, lang = 'en'):
    try:
        games = database.get_last_results(tele_id, mode)
        logger.info("connected to db. got last 5 games in single " + mode)
    except Exception as e:
        logger.error(e)
    length = len(games)
    mean_scores = []
    for i in range(length):
        total_score = 0
        counter = 0
        for j in range(max(0, i - 19), i + 1):
            counter += 1
            total_score += games[j][0]
        mean_scores.append(total_score / counter)
    plt.plot(np.arange(1, len(mean_scores) + 1), mean_scores)
    plt.savefig(f"./tmp/{tele_id}.png")
    plt.clf()

if __name__ == "__main__":
    form_statistics_graph(679428900, "msk")