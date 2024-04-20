import os
import logging

from pymongo import MongoClient
from urllib.parse import quote_plus as quote
from dotenv import load_dotenv
from coords_generator import generate_seed

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('GEOGESSER')
logger.setLevel(logging.DEBUG)

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
URL = 'mongodb://{user}:{pw}@{hosts}/?authSource={authsrc}'.format(
    user=quote(DB_USER),
    pw=quote(DB_PASS),
    hosts=DB_HOST,
    authsrc = "admin"
    )

async def add_user(tele_id, username):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    user = {
        "tele_id" : tele_id,
        "username" : username,
        "language" : "en",
        "seed_msk" : "",
        "seed_spb" : "",
        "seed_rus" : "",
        "seed_blrs" : "",
        "is_active_session_msk" : False,
        "is_active_session_spb" : False,
        "is_active_session_rus" : False,
        "is_active_session_blrs" : False,
        # "msk_single_total_score" : 0,
        # "msk_single_game_counter": 0,
        # "msk_single_mean_score" : 0,
        # "last_games_msk" : [],
        # "spb_single_total_score" : 0,
        # "spb_single_game_counter" : 0,
        # "spb_single_mean_score" : 0,
        # "last_games_spb" : [],
        # "rus_single_total_score" : 0,
        # "rus_single_game_counter" : 0,
        # "rus_single_mean_score" : 0,
        # "last_games_rus" : []
    }
    
    users.insert_one(user)

    conn.close()

async def find_user(tele_id):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    find_user = users.find_one({"tele_id" : tele_id})

    if find_user:
        conn.close()
        return True
    
    conn.close()
    return False

async def delete_database():
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    users.delete_many({})

    conn.close()

async def show_database():
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    for user in users.find():
        print(user)

    conn.close()

async def set_seed(tele_id, seed, mode):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    users.update_one({"tele_id" : tele_id}, {"$set" : {"seed_" + mode : seed}})

    conn.close()

async def get_seed(tele_id, mode):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    user = users.find_one({"tele_id" : tele_id})
    seed = user["seed_" + mode]

    conn.close()
    return seed

async def init_game(tele_id, mode):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    user = users.find_one({"tele_id" : tele_id})
    if not(user["is_active_session_" + mode]):
        await set_seed(tele_id, generate_seed())

    users.update_one({"tele_id" : tele_id}, {"$set" : {"is_active_session_" + mode : True}})
    conn.close()

async def end_game(tele_id, mode):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    users.update_one({"tele_id" : tele_id}, {"$set" : {"is_active_session_" + mode : False}})
    conn.close()

async def get_top10_single(mode):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users


    for user in users.find():
        if (mode.lower() +"_single_mean_score" not in user.keys()):
            users.update_one({"tele_id" : user["tele_id"]}, {"$set" : {mode.lower() +"_single_mean_score" : 0}})
            users.update_one({"tele_id" : user["tele_id"]}, {"$set" : {mode.lower() +"_single_game_counter" : 0}})
            users.update_one({"tele_id" : user["tele_id"]}, {"$set" : {mode.lower() +"_single_total_score" : 0}})
    logger.info("updated db. added column with single " + mode)

    sort = {"$sort":
            {mode.lower() +"_single_mean_score" : -1}
            }
    limit = {"$limit":10}

    res = list(users.aggregate([sort, limit]))
    conn.close()
    return res


async def add_results_single(tele_id, score, mode):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    
    user = users.find_one({"tele_id" : tele_id})
    if mode.lower() +"_single_total_score" not in user.keys():
        users.update_one({"tele_id" : tele_id}, {'$set': {mode.lower() +"_single_total_score": 0}})
    if mode.lower() +"_single_game_counter" not in user.keys():
        users.update_one({"tele_id" : tele_id}, {'$set': {mode.lower() +"_single_game_counter": 0}})

    users.update_one({"tele_id" : tele_id}, {'$inc': {mode.lower() +"_single_total_score": score}})
    users.update_one({"tele_id" : tele_id}, {'$inc': {mode.lower() +"_single_game_counter": 1}})

    user = users.find_one({"tele_id" : tele_id})
    mean_score = round(user[mode.lower() +"_single_total_score"] / user[mode.lower() +"_single_game_counter"], 2)
    users.update_one({"tele_id" : tele_id}, {'$set': {mode.lower() +"_single_mean_score": mean_score}})
    
    conn.close()

async def drop_duplicates():
    pass

async def get_last5_results(tele_id, mode):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    user = users.find_one({"tele_id" : tele_id})
    if "last_games_" + mode.lower() not in user:
        users.update_one({"tele_id" : tele_id}, {"$set" : {"last_games_" + mode.lower() : []}})
        user = users.find_one({"tele_id" : tele_id})

    games = user["last_games_" + mode.lower()]
    conn.close()
    return games

async def add_game_single(tele_id, score, metres, mode):

    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    user = users.find_one({"tele_id" : tele_id})
    if "last_games_" + mode.lower() not in user:
        users.update_one({"tele_id" : tele_id}, {"$set" : {"last_games_" + mode.lower() : []}})
        user = users.find_one({"tele_id" : tele_id})

    games = user["last_games_" + mode.lower()]
    if (len(games) < 5):
        games.insert(0, (score, metres))
    else:
        games.pop(-1)
        games.insert(0, (score, metres))
    users.update_one({"tele_id" : tele_id}, {"$set" : {"last_games_" + mode.lower() : games}})

    conn.close()

async def set_language(tele_id, language):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    users.update_one(filter = {"tele_id" : tele_id}, update = {'$set': {'language': language}})

    conn.close()

async def get_language(tele_id):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    user = users.find_one({"tele_id" : tele_id})
    if "language" not in user:
        users.update_one({"tele_id" : tele_id}, {"$set" : {"language", "en"}})
        user = users.find_one({"tele_id" : tele_id})

    conn.close()
    return user["language"]
