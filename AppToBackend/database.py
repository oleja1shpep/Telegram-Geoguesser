import os

from pymongo import MongoClient
from urllib.parse import quote_plus as quote
from dotenv import load_dotenv

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

    def is_active_session(self, tele_id, mode):
        user = self.users.find_one({"tele_id" : tele_id})
        return user and f"is_active_session_{mode}" in user and user[f"is_active_session_{mode}"]
    
    def end_solo_game(self, data):
        user = self.users.find_one({"tele_id": data['tele_id']})
        self.users.update_one({"tele_id": data['tele_id']}, 
                                {"$set": {
                                    f'is_active_session_{data['mode']}': not user["track_changes"],
                                    f'color_scheme': data['fields']['color_scheme']
                                  } |
                                  {f'{data['mode']}_{key}': value for key, value in data['fields'].items()}
                                })    

    def get_test(self, tele_id):
        user = self.users.find_one({"tele_id": tele_id})
        if not user:
            return None
        del user["_id"]
        return user
    
    def set_test(self, tele_id, mode, seed_msk, track_changes):
        self.users.insert_one({"tele_id": tele_id, "mode": mode, "seed_msk": seed_msk, "track_changes": track_changes})
