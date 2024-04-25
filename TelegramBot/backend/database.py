import os
import logging

from pymongo import MongoClient
from urllib.parse import quote_plus as quote
from dotenv import load_dotenv
from backend.seed_processor import generate_seed

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

def add_user(tele_id, username):
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

def check_key(tele_id, key):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    user = users.find_one({"tele_id" : tele_id})
    
    if key in user:
        conn.close()
        return True
    conn.close()
    return False

def set_key(tele_id, key, value):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    users.update_one({"tele_id" : tele_id}, {"$set" : {key : value}})
    conn.close()

def inc_key(tele_id, key, value, default = 0):
    if not(check_key(tele_id, key)):
        set_key(tele_id, key, default)
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    users.update_one({"tele_id" : tele_id}, {"$inc" : {key : value}})
    conn.close()

def get_key(tele_id, key, default):
    if not(check_key(tele_id, key)):
        set_key(tele_id, key, default)

    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    user = users.find_one({"tele_id" : tele_id})
    res = user[key]
    conn.close()
    return res
    
def find_user(tele_id):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    find_user = users.find_one({"tele_id" : tele_id})

    if find_user:
        conn.close()
        return True
    
    conn.close()
    return False

def delete_database():
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    users.delete_many({})

    conn.close()

def show_database():
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    for user in users.find():
        print(user)

    conn.close()

def set_seed(tele_id, seed, mode):
    set_key(tele_id, "seed_" + mode, seed)


def get_seed(tele_id, mode):
    seed = get_key(tele_id, "seed_" + mode, "")
    return seed

def set_track_changes(tele_id, mode, value):
    set_key(tele_id, "track_changes_" + mode, value)

def get_track_changes(tele_id, mode):
    return get_key(tele_id, "track_changes_" + mode, True)

def init_game(tele_id, mode):
    set_track_changes(tele_id, mode, True)
    if not(get_key(tele_id, "is_active_session_" + mode, False)):
        set_seed(tele_id, generate_seed(), mode)
    set_key(tele_id, "is_active_session_" + mode, True)


def end_game(tele_id, mode):
    set_key(tele_id, "is_active_session_" + mode, False)


def get_top10_single(mode):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    for user in users.find():
        if (mode.lower() +"_single_mean_score" not in user.keys()):
            set_key(user["tele_id"], mode +"_single_mean_score", 0)
            set_key(user["tele_id"], mode +"_single_game_counter", 0)
            set_key(user["tele_id"], mode +"_single_total_score", 0)
    logger.info("updated db. added column with single " + mode)

    sort = {"$sort":
            {mode.lower() +"_single_mean_score" : -1}
            }
    limit = {"$limit":10}

    res = list(users.aggregate([sort, limit]))
    conn.close()
    return res


def add_results_single(tele_id, score, mode):
    inc_key(tele_id, mode + "_single_total_score", score)
    inc_key(tele_id, mode + "_single_game_counter", 1)
    
    try:
        mean_score = round(get_key(tele_id, mode + "_single_total_score", 0) / get_key(tele_id, mode + "_single_game_counter", 0) ,2)
    except:
        mean_score = 0

    set_key(tele_id, mode +"_single_mean_score", mean_score)
    
def drop_duplicates():
    pass

def get_last5_results(tele_id, mode):
    games = get_key(tele_id, "last_games_" + mode, [])
    return games

def add_game_single(tele_id, score, metres, mode):
    games = get_last5_results(tele_id, mode)

    if (len(games) < 5):
        games.insert(0, (score, metres))
    else:
        games.pop(-1)
        games.insert(0, (score, metres))

    set_key(tele_id, "last_games_" + mode, games)


def set_language(tele_id, language):
    set_key(tele_id, 'language', language)

def get_language(tele_id):
    return get_key(tele_id, "language", 'en')

def switch_gpt(tele_id):
    res = get_key(tele_id, "use_gpt", False)
    set_key(tele_id, "use_gpt", not(res))

def get_gpt(tele_id):
    return get_key(tele_id, "use_gpt", True)

def set_multiplayer_seed(tele_id, seed, mode):
    set_key(tele_id, "mul_seed_" + mode, seed)

def get_multiplayer_seed(tele_id, mode):
    return get_key(tele_id, "mul_seed_" + mode, "")

def set_state(tele_id, state):
    set_key(tele_id, "state", state)

def get_state(tele_id):
    if (find_user(tele_id)):
        state = get_key(tele_id, "state", "menu")
        logger.debug(f"state: {state}")
        return state
    else:
        return "start"


def set_state_data(tele_id, data):
    set_key(tele_id, "state_data", data)

def get_state_data(tele_id):
    return get_key(tele_id, "state_data", "")

