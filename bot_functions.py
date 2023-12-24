from math import cos, sin, asin, sqrt, radians, log
from config import TOKEN_BOT, TOKEN_STATIC
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

def get_top10_moscow_single():
    top_10_users = database.get_top10_moscow_single()
    txt = ''
    for i in range(len(top_10_users)):
        txt += f'{i+1}. {top_10_users[i][0]} - среднее : {top_10_users[i][3]} | матчей : {top_10_users[i][2]}\n'
    print(top_10_users)
    return txt

def get_top10_spb_single():
    top_10_users = database.get_top10_spb_single()
    txt = ''
    for i in range(len(top_10_users)):
        txt += f'{i+1}. {top_10_users[i][0]} - среднее : {top_10_users[i][3]} | матчей : {top_10_users[i][2]}\n'
    print(top_10_users)
    return txt

def get_top10_russia_single():
    top_10_users = database.get_top10_russia_single()
    txt = ''
    for i in range(len(top_10_users)):
        txt += f'{i+1}. {top_10_users[i][0]} - среднее : {top_10_users[i][3]} | матчей : {top_10_users[i][2]}\n'
    print(top_10_users)
    return txt