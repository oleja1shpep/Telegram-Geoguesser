import os
import logging
import json

from datetime import date, timedelta
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

class MongoDB:

    def __init__(self):
        self.conn = MongoClient(URL)
        self.db = self.conn[DB_NAME]
        self.users = self.db.users
    def close(self):
        self.conn.close()

    def add_user(self, tele_id, username):
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
        
        self.users.insert_one(user)

    def delete_user(self, tele_id):
        self.users.delete_many({"tele_id" : tele_id})

    def get_user(self, username):
        user = self.users.find_one({"username" : username})
        return user

    def check_key(self, tele_id, key):
        user = self.users.find_one({"tele_id" : tele_id})

        if key in user:
            return True
        return False

    def set_key(self, tele_id, key, value):
        self.users.update_one({"tele_id" : tele_id}, {"$set" : {key : value}})

    def inc_key(self, tele_id, key, value, default = 0):
        if not(self.check_key(tele_id, key)):
            self.set_key(tele_id, key, default)
        self.users.update_one({"tele_id" : tele_id}, {"$inc" : {key : value}})

    def get_key(self, tele_id, key, default):
        if not(self.check_key(tele_id, key)):
            self.set_key(tele_id, key, default)

        user = self.users.find_one({"tele_id" : tele_id})
        res = user[key]
        return res
        
    def find_user(self, tele_id):
        find_user = self.users.find_one({"tele_id" : tele_id})

        if find_user:
            return True
        return False

    def delete_database(self):
        self.users.delete_many({})

    def show_database(self):
        for user in self.users.find():
            print(user)

    def init_game(self, tele_id, mode):
        self.set_key(tele_id, "track_changes", True)
        if not(self.get_key(tele_id, "is_active_session_" + mode, False)):
            self.set_key(tele_id, "seed_" + mode, generate_seed())
        self.set_key(tele_id, "is_active_session_" + mode, True)

    def end_game(self, tele_id, mode):
        self.set_key(tele_id, "is_active_session_" + mode, False)

    def get_top10_single(self, mode):

        for user in self.users.find():
            if (mode.lower() +"_single_mean_score" not in user.keys()):
                self.set_key(user["tele_id"], mode +"_single_mean_score", 0)
                self.set_key(user["tele_id"], mode +"_single_game_counter", 0)
                self.set_key(user["tele_id"], mode +"_single_total_score", 0)
        logger.info("updated db. added column with single " + mode)

        sort = {"$sort":
                {mode.lower() +"_single_mean_score" : -1}
                }
        limit = {"$limit":10}

        res = list(self.users.aggregate([sort, limit]))
        return res

    def add_results_single(self, tele_id, score, mode):
        self.inc_key(tele_id, mode + "_single_total_score", score)
        self.inc_key(tele_id, mode + "_single_game_counter", 1)
        
        try:
            mean_score = round(self.get_key(tele_id, mode + "_single_total_score", 0) / self.get_key(tele_id, mode + "_single_game_counter", 0) ,2)
        except:
            mean_score = 0

        self.set_key(tele_id, mode +"_single_mean_score", mean_score)
        
    def drop_duplicates(self):
        pass

    def get_last5_results(self, tele_id, mode):
        games = self.get_key(tele_id, "last_games_" + mode, [])
        if (type(games) == str):
            games = json.loads(games)
        return games

    def add_game_single(self, tele_id, score, metres, mode):
        games = self.get_last5_results(tele_id, mode)
        if (type(games) == str):
            games = json.loads(games)

        if (len(games) < 5):
            games.insert(0, (score, metres))
        else:
            games.pop(-1)
            games.insert(0, (score, metres))

        self.set_key(tele_id, "last_games_" + mode, games)

    def get_state(self, tele_id):
        if (self.find_user(tele_id)):
            state = self.get_key(tele_id, "state", "start")
            # logger.debug(f"state: {state}")
            return state
        else:
            return "start"