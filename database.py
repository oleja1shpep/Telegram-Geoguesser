import sqlite3
from config import DB_NAME
import json

def search_tele_id(tele_id, tele_username):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    
    find_login = cur.execute("SELECT tele_id FROM users_state WHERE tele_id = ?", (tele_id, ))
    if (find_login.fetchone() == None):
        cur.execute("""INSERT INTO users_state VALUES
                    (?, ?, 0, 0, 0, '[]', 0, 0, 0, '[]', 0, 0, 0, '[]')
                    """, (tele_id, tele_username, ))
        connection.commit()
        connection.close()
        return False
    connection.close()
    return True

def get_top10_moscow_single():
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    rows = cur.execute("SELECT username, moscow_single_total_score, moscow_single_game_counter, moscow_single_mean_score FROM users_state ORDER BY moscow_single_mean_score DESC")
    res = rows.fetchmany(10)
    connection.close()
    return res

def get_top10_spb_single():
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    rows = cur.execute("SELECT username, spb_single_total_score, spb_single_game_counter, spb_single_mean_score FROM users_state ORDER BY spb_single_mean_score DESC")
    res = rows.fetchmany(10)
    connection.close()
    return res

def get_top10_russia_single():
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    rows = cur.execute("SELECT username, russia_single_total_score, russia_single_game_counter, russia_single_mean_score FROM users_state ORDER BY russia_single_mean_score DESC")
    res = rows.fetchmany(10)
    connection.close()
    return res

def get_top10_belarus_single():
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    rows = cur.execute("SELECT username, belarus_single_total_score, belarus_single_game_counter, belarus_single_mean_score FROM users_state ORDER BY belarus_single_mean_score DESC")
    res = rows.fetchmany(10)
    connection.close()
    return res

def add_results_moscow_single(tele_id, score):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    user_data = cur.execute("SELECT tele_id, username, moscow_single_total_score, moscow_single_game_counter, moscow_single_mean_score FROM users_state WHERE tele_id = ?", (tele_id, ))
    user_data = user_data.fetchone()
    cur = connection.cursor()
    game_counter = user_data[3]
    current_score = user_data[2]
    if game_counter == None:
        game_counter = 0
    if current_score == None:
        current_score = 0

    cur.execute("UPDATE users_state SET moscow_single_game_counter = ?, moscow_single_total_score = ?, moscow_single_mean_score = ? WHERE tele_id = ?", (game_counter + 1, current_score + score, round((current_score + score) / (game_counter + 1),2) , tele_id, ))
    connection.commit()

    connection.close()

def add_results_spb_single(tele_id, score):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    user_data = cur.execute("SELECT tele_id, username, spb_single_total_score, spb_single_game_counter, spb_single_mean_score FROM users_state WHERE tele_id = ?", (tele_id, ))
    user_data = user_data.fetchone()
    cur = connection.cursor()

    game_counter = user_data[3]
    current_score = user_data[2]
    if game_counter == None:
        game_counter = 0
    if current_score == None:
        current_score = 0
    cur.execute("UPDATE users_state SET spb_single_game_counter = ?, spb_single_total_score = ?, spb_single_mean_score = ? WHERE tele_id = ?", (game_counter + 1, current_score + score, round((current_score + score) / (game_counter + 1),2) , tele_id, ))
    connection.commit()

    connection.close()

def add_results_russia_single(tele_id, score):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    user_data = cur.execute("SELECT tele_id, username, russia_single_total_score, russia_single_game_counter, russia_single_mean_score FROM users_state WHERE tele_id = ?", (tele_id, ))
    user_data = user_data.fetchone()
    cur = connection.cursor()
    game_counter = user_data[3]
    current_score = user_data[2]
    if game_counter == None:
        game_counter = 0
    if current_score == None:
        current_score = 0
    cur.execute("UPDATE users_state SET russia_single_game_counter = ?, russia_single_total_score = ?, russia_single_mean_score = ? WHERE tele_id = ?", (game_counter + 1, current_score + score, round((current_score + score) / (game_counter + 1),2) , tele_id, ))
    connection.commit()

    connection.close()

def add_results_belarus_single(tele_id, score):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    user_data = cur.execute("SELECT tele_id, username, belarus_single_total_score, belarus_single_game_counter, belarus_single_mean_score FROM users_state WHERE tele_id = ?", (tele_id, ))
    user_data = user_data.fetchone()
    cur = connection.cursor()
    game_counter = user_data[3]
    current_score = user_data[2]
    if game_counter == None:
        game_counter = 0
    if current_score == None:
        current_score = 0
    cur.execute("UPDATE users_state SET belarus_single_game_counter = ?, belarus_single_total_score = ?, belarus_single_mean_score = ? WHERE tele_id = ?", (game_counter + 1, current_score + score, round((current_score + score) / (game_counter + 1),2) , tele_id, ))
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

def get_last5_results_moscow(tele_id):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute("SELECT tele_id, last_games_moscow FROM users_state WHERE tele_id = ?", (tele_id, ))
    res = cur.fetchone()
    games = json.loads(res[1])
    #print(res)
    connection.close()
    return games

def get_last5_results_spb(tele_id):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute("SELECT tele_id, last_games_spb FROM users_state WHERE tele_id = ?", (tele_id, ))
    res = cur.fetchone()
    games = json.loads(res[1])
    #print(res)
    connection.close()
    return games

def get_last5_results_russia(tele_id):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute("SELECT tele_id, last_games_russia FROM users_state WHERE tele_id = ?", (tele_id, ))
    res = cur.fetchone()
    games = json.loads(res[1])
    #print(res)
    connection.close()
    return games

def get_last5_results_belarus(tele_id):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute("SELECT tele_id, last_games_belarus FROM users_state WHERE tele_id = ?", (tele_id, ))
    res = cur.fetchone()
    games = json.loads(res[1])
    #print(res)
    connection.close()
    return games

def add_game_moscow_single(tele_id, score, metres):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute("SELECT tele_id, last_games_moscow FROM users_state WHERE tele_id = ?", (tele_id, ))
    games = json.loads(cur.fetchone()[1])
    if (len(games) < 5):
        games.insert(0, (score, metres))
    else:
        games.pop(-1)
        games.insert(0, (score, metres))
    cur.execute("UPDATE users_state SET last_games_moscow = ? WHERE tele_id = ?", (json.dumps(games),tele_id, ))
    connection.commit()
    connection.close()

def add_game_spb_single(tele_id, score, metres):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute("SELECT tele_id, last_games_spb FROM users_state WHERE tele_id = ?", (tele_id, ))
    games = json.loads(cur.fetchone()[1])
    if (len(games) < 5):
        games.insert(0, (score, metres))
    else:
        games.pop(-1)
        games.insert(0, (score, metres))
    cur.execute("UPDATE users_state SET last_games_spb = ? WHERE tele_id = ?", (json.dumps(games),tele_id, ))
    connection.commit()
    connection.close()

def add_game_russia_single(tele_id, score, metres):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute("SELECT tele_id, last_games_russia FROM users_state WHERE tele_id = ?", (tele_id, ))
    games = json.loads(cur.fetchone()[1])
    if (len(games) < 5):
        games.insert(0, (score, metres))
    else:
        games.pop(-1)
        games.insert(0, (score, metres))
    cur.execute("UPDATE users_state SET last_games_russia = ? WHERE tele_id = ?", (json.dumps(games),tele_id, ))
    connection.commit()
    connection.close()

def add_game_belarus_single(tele_id, score, metres):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute("SELECT tele_id, last_games_belarus FROM users_state WHERE tele_id = ?", (tele_id, ))
    games = json.loads(cur.fetchone()[1])
    if (len(games) < 5):
        games.insert(0, (score, metres))
    else:
        games.pop(-1)
        games.insert(0, (score, metres))
    cur.execute("UPDATE users_state SET last_games_belarus = ? WHERE tele_id = ?", (json.dumps(games),tele_id, ))
    connection.commit()
    connection.close()


# connection = sqlite3.connect(DB_NAME)
# cur = connection.cursor()

# cur.execute("ALTER TABLE users_state ADD COLUMN mean_score")
# connection.commit()
# connection.close()

