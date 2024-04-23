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

async def check_key(tele_id, key):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    user = users.find_one({"tele_id" : tele_id})
    
    if key in user:
        conn.close()
        return True
    conn.close()
    return False

async def set_key(tele_id, key, value):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    users.update_one({"tele_id" : tele_id}, {"$set" : {key : value}})
    conn.close()

async def inc_key(tele_id, key, value, default = 0):
    if not(await check_key(tele_id, key)):
        await set_key(tele_id, key, default)
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    users.update_one({"tele_id" : tele_id}, {"$inc" : {key : value}})
    conn.close()

async def get_key(tele_id, key, default):
    if not(await check_key(tele_id, key)):
        await set_key(tele_id, key, default)

    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    user = users.find_one({"tele_id" : tele_id})
    res = user[key]
    conn.close()
    return res
    
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
    await set_key(tele_id, "seed_" + mode, seed)


async def get_seed(tele_id, mode):
    seed = await get_key(tele_id, "seed_" + mode, "")
    return seed

async def init_game(tele_id, mode):
    if not(await get_key(tele_id, "is_active_session_" + mode, False)):
        await set_seed(tele_id, generate_seed(), mode)
    await set_key(tele_id, "is_active_session_" + mode, True)


async def end_game(tele_id, mode):
    await set_key(tele_id, "is_active_session_" + mode, False)


async def get_top10_single(mode):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    for user in users.find():
        if (mode.lower() +"_single_mean_score" not in user.keys()):
            await set_key(user["tele_id"], mode +"_single_mean_score", 0)
            await set_key(user["tele_id"], mode +"_single_game_counter", 0)
            await set_key(user["tele_id"], mode +"_single_total_score", 0)
    logger.info("updated db. added column with single " + mode)

    sort = {"$sort":
            {mode.lower() +"_single_mean_score" : -1}
            }
    limit = {"$limit":10}

    res = list(users.aggregate([sort, limit]))
    conn.close()
    return res


async def add_results_single(tele_id, score, mode):
    await inc_key(tele_id, mode + "_single_total_score", score)
    await inc_key(tele_id, mode + "_single_game_counter", 1)
    
    try:
        mean_score = round(await get_key(tele_id, mode + "_single_total_score", 0) / await get_key(tele_id, mode + "_single_game_counter", 0) ,2)
    except:
        mean_score = 0

    await set_key(tele_id, mode +"_single_mean_score", mean_score)
    
async def drop_duplicates():
    pass

async def get_last5_results(tele_id, mode):
    games = await get_key(tele_id, "last_games_" + mode, [])
    return games

async def add_game_single(tele_id, score, metres, mode):
    games = await get_last5_results(tele_id, mode)

    if (len(games) < 5):
        games.insert(0, (score, metres))
    else:
        games.pop(-1)
        games.insert(0, (score, metres))

    await set_key(tele_id, "last_games_" + mode, games)


async def set_language(tele_id, language):
    await set_key(tele_id, 'language', language)

async def get_language(tele_id):
    return await get_key(tele_id, "language", 'en')

async def switch_gpt(tele_id):
    res = await get_key(tele_id, "use_gpt", False)
    await set_key(tele_id, "use_gpt", not(res))

async def get_gpt(tele_id):
    return await get_key(tele_id, "use_gpt", True)