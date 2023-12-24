from math import cos, sin, asin, sqrt, radians, log
from config import TOKEN_STATIC
import database

def get_url(cords):
    lat1, lon1, _, lat2, lon2 = map(float, cords.split())
    return f"https://static-maps.yandex.ru/v1?pl=c:8822DDC0,w:3,{lon1},{lat1},{lon2},{lat2}&pt={lon1},{lat1},flag~{lon2},{lat2},comma&apikey={TOKEN_STATIC}"

def calculate_score_and_distance(cords):
    lat1, lon1, _, lat2, lon2 = map(float, cords.split())

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    metres = 6371 * c * 1000
    score = max(min(-log(metres / 70, 1.0014) + 5000, 5000), 0)
    return [int(score), int(metres)]

def calculate_score_and_distance_moscow_spb(cords):
    lat1, lon1, _, lat2, lon2 = map(float, cords.split())

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    metres = 6371 * c * 1000
    score = max(min(5000-log((metres + 90)/ 100, 1.001), 5000), 0)
    return [int(score), int(metres)]

def calculate_score_and_distance_russia(cords):
    lat1, lon1, _, lat2, lon2 = map(float, cords.split())

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    metres = 6371 * c * 1000
    score = max(min(5000-log((metres + 29000)/ 3000, 1.00141), 5000), 0)
    return [int(score), int(metres)]

def create_result_text(score, metres):
    txt = ""
    if metres < 10000:
        txt = f"Вы набрали {score} очков\nРасстояние {metres} метров"
    elif metres < 100000:
        txt = f"Вы набрали {score} очков\nРасстояние {round(metres / 1000, 2)} километров"
    else:
        txt = f"Вы набрали {score} очков\nРасстояние {round(metres / 1000, 0)} километров"
    
    return txt

def get_top10_moscow_single():
    top_10_users = database.get_top10_moscow_single()
    txt = ''
    for i in range(len(top_10_users)):
        txt += f'{i+1}. {top_10_users[i][0]} - среднее : {top_10_users[i][3]} | матчей : {top_10_users[i][2]}\n'
    #print(top_10_users)
    return txt

def get_top10_spb_single():
    top_10_users = database.get_top10_spb_single()
    txt = ''
    for i in range(len(top_10_users)):
        txt += f'{i+1}. {top_10_users[i][0]} - среднее : {top_10_users[i][3]} | матчей : {top_10_users[i][2]}\n'
    #print(top_10_users)
    return txt

def get_top10_russia_single():
    top_10_users = database.get_top10_russia_single()
    txt = ''
    for i in range(len(top_10_users)):
        txt += f'{i+1}. {top_10_users[i][0]} - среднее : {top_10_users[i][3]} | матчей : {top_10_users[i][2]}\n'
    #print(top_10_users)
    return txt

def get_last5_results_moscow_single(tele_id):
    games = database.get_last5_results_moscow(tele_id=tele_id)
    txt = ''
    for i in range(len(games)):
        txt += f"{i+1}. {games[i][0]} очков | {games[i][1]} метров\n"
    if len(games) == 0:
        txt = "Вы ещё не сыграли ни одну игру"
    return txt

def get_last5_results_spb_single(tele_id):
    games = database.get_last5_results_spb(tele_id=tele_id)
    txt = ''
    for i in range(len(games)):
        txt += f"{i+1}. {games[i][0]} очков | {games[i][1]} метров\n"
    if len(games) == 0:
        txt = "Вы ещё не сыграли ни одну игру"
    return txt

def get_last5_results_russia_single(tele_id):
    games = database.get_last5_results_russia(tele_id=tele_id)
    txt = ''
    for i in range(len(games)):
        txt += f"{i+1}. {games[i][0]} очков | {games[i][1]} метров\n"
    if len(games) == 0:
        txt = "Вы ещё не сыграли ни одну игру"
    return txt