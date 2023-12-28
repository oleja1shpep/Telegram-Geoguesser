import sqlite3
from config import DB_NAME
import json

def search_tele_id(tele_id, tele_username):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    
    find_login = cur.execute("SELECT tele_id FROM users_state WHERE tele_id = ?", (tele_id, ))
    if (find_login.fetchone() == None):
        cur.execute("""INSERT INTO users_state VALUES
                    (?, ?, 0, 0, 0, '[]', 0, 0, 0, '[]', 0, 0, 0, '[]', 0, 0, 0, '[]')
                    """, (tele_id, tele_username, ))
        connection.commit()
        connection.close()
        return False
    connection.close()
    return True

def get_top10_single(mode):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    rows = cur.execute("SELECT username, "+ mode.lower() +"_single_total_score, "+ mode.lower() +"_single_game_counter, "+ mode.lower() +"_single_mean_score FROM users_state ORDER BY "+ mode.lower() +"_single_mean_score DESC")
    res = rows.fetchmany(10)
    connection.close()
    return res

def add_results_single(tele_id, score, mode):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    user_data = cur.execute("SELECT tele_id, username, "+ mode.lower() +"_single_total_score, "+ mode.lower() +"_single_game_counter, "+ mode.lower() +"_single_mean_score FROM users_state WHERE tele_id = ?", (tele_id, ))
    user_data = user_data.fetchone()
    cur = connection.cursor()
    game_counter = user_data[3]
    current_score = user_data[2]
    if game_counter == None:
        game_counter = 0
    if current_score == None:
        current_score = 0

    cur.execute("UPDATE users_state SET "+ mode.lower() +"_single_game_counter = ?, "+ mode.lower() +"_single_total_score = ?, "+ mode.lower() +"_single_mean_score = ? WHERE tele_id = ?", (game_counter + 1, current_score + score, round((current_score + score) / (game_counter + 1),2) , tele_id, ))
    connection.commit()

    connection.close()

def drop_duplicates():
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute("""
    DELETE FROM users_state
    WHERE rowid > (
    SELECT MIN(rowid) FROM users_state p2  
    WHERE users_state.tele_id = p2.tele_id
    AND users_state.username = p2.username
    );
    """)
    connection.commit()
    connection.close()

def get_last5_results(tele_id, mode):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute("SELECT tele_id, last_games_" + mode.lower() + " FROM users_state WHERE tele_id = ?", (tele_id, ))
    res = cur.fetchone()
    games = json.loads(res[1])
    #print(res)
    connection.close()
    return games

def add_game_single(tele_id, score, metres, mode):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute("SELECT tele_id, last_games_" + mode.lower() + " FROM users_state WHERE tele_id = ?", (tele_id, ))
    games = json.loads(cur.fetchone()[1])
    if (len(games) < 5):
        games.insert(0, (score, metres))
    else:
        games.pop(-1)
        games.insert(0, (score, metres))
    cur.execute("UPDATE users_state SET last_games_" + mode.lower() + " = ? WHERE tele_id = ?", (json.dumps(games),tele_id, ))
    connection.commit()
    connection.close()

# connection = sqlite3.connect(DB_NAME)
# cur = connection.cursor()

# cur.execute("ALTER TABLE users_state ADD COLUMN mean_score")
# connection.commit()
# connection.close()

