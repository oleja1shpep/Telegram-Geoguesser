import sqlite3
import os
from pymongo import MongoClient
from config import DB_NAME
from urllib.parse import quote_plus as quote
import json

DB_HOST = os.getenv("DB_HOST") or "localhost"
DB_USER = os.getenv("DB_USER") or "mongo"
DB_PASS = os.getenv("DB_PASS") or "mongomongo"
URL = 'mongodb://{user}:{pw}@{hosts}/?authSource=admin'.format(
    user=quote(DB_USER),
    pw=quote(DB_PASS),
    hosts=DB_HOST,
    )

def add_user(tele_id, username):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users

    user = {
        "tele_id" : tele_id,
        "username" : username,
        # "language" : "en",
        # "moscow_single_total_score" : 0,
        # "moscow_single_game_counter": 0,
        # "moscow_single_mean_score" : 0,
        # "last_games_moscow" : [],
        # "spb_single_total_score" : 0,
        # "spb_single_game_counter" : 0,
        # "spb_single_mean_score" : 0,
        # "last_games_spb" : [],
        # "russia_single_total_score" : 0,
        # "russia_single_game_counter" : 0,
        # "russia_single_mean_score" : 0,
        # "last_games_russia" : []
    }
    
    users.insert_one(user)

    conn.close()

async def search_tele_id(tele_id, username):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    find_user = users.find_one({"tele_id" : tele_id})

    if find_user:
        conn.close()
        return True
    
    add_user(tele_id, username)
    conn.close()
    return False


async def get_top10_single(mode):
    conn = MongoClient(URL)
    db = conn[DB_NAME]
    users = db.users
    users_without_key = []
    for user in users.find():
        if (mode.lower() +"_single_mean_score" not in user.keys()):
            users.update_one({"tele_id" : user["tele_id"]}, {"$set" : {mode.lower() +"_single_mean_score" : 0}})
            users.update_one({"tele_id" : user["tele_id"]}, {"$set" : {mode.lower() +"_single_game_counter" : 0}})
            users.update_one({"tele_id" : user["tele_id"]}, {"$set" : {mode.lower() +"_single_total_score" : 0}})

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
