import sqlite3
from config import DB_NAME

def search_tele_id(tele_id, tele_username):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    
    find_login = cur.execute("SELECT tele_id FROM users_state WHERE tele_id = ?", (tele_id, ))
    if (find_login.fetchone() == None):
        cur.execute("""INSERT INTO users_state VALUES
                    (?, ?, 0, 0, 0, 0, 0, 0)
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

def get_top10_world_single():
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    rows = cur.execute("SELECT username, world_single_total_score, world_single_game_counter, world_single_mean_score FROM users_state ORDER BY world_single_mean_score DESC")
    res = rows.fetchmany(10)
    connection.close()
    return res

def add_results_moscow_single(tele_id, score):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    user_data = cur.execute("SELECT tele_id, username, moscow_single_total_score, moscow_single_game_counter, moscow_single_mean_score FROM users_state WHERE tele_id = ?", (tele_id, ))
    user_data = user_data.fetchone()
    cur = connection.cursor()
    cur.execute("UPDATE users_state SET moscow_single_game_counter = ?, moscow_single_total_score = ?, moscow_single_mean_score = ? WHERE tele_id = ?", (user_data[3] + 1, user_data[2] + score, round((user_data[2] + score) / (user_data[3] + 1),2) , tele_id, ))
    connection.commit()

    connection.close()

def add_results_world_single(tele_id, score):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    user_data = cur.execute("SELECT tele_id, username, world_single_total_score, world_single_game_counter, world_single_mean_score FROM users_state WHERE tele_id = ?", (tele_id, ))
    user_data = user_data.fetchone()
    cur = connection.cursor()
    cur.execute("UPDATE users_state SET world_single_game_counter = ?, world_single_total_score = ?, world_single_mean_score = ? WHERE tele_id = ?", (user_data[3] + 1, user_data[2] + score, round((user_data[2] + score) / (user_data[3] + 1),2) , tele_id, ))
    connection.commit()

    connection.close()



# connection = sqlite3.connect(DB_NAME)
# cur = connection.cursor()

# cur.execute("ALTER TABLE users_state ADD COLUMN mean_score")
# connection.commit()
# connection.close()
