import sqlite3
from config import DB_NAME


def search_tele_id(tele_id, tele_username):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    
    find_login = cur.execute("SELECT tele_id FROM users_state WHERE tele_id = ?", (tele_id, ))
    if (find_login.fetchone() == None):
        cur.execute("""INSERT INTO users_state VALUES
                    (?, ?, 0, 0, 0)
                    """, (tele_id, tele_username, ))
        connection.commit()
        connection.close()
        return False
    connection.close()
    return True


def get_top10():
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    rows = cur.execute("SELECT username, total_score, game_counter, mean_score FROM users_state ORDER BY mean_score DESC")
    res = rows.fetchmany(10)
    connection.close()
    return res

def add_results(tele_id, score):
    connection = sqlite3.connect(DB_NAME)
    cur = connection.cursor()
    user_data = cur.execute("SELECT tele_id, username, total_score, game_counter, mean_score FROM users_state WHERE tele_id = ?", (tele_id, ))
    user_data = user_data.fetchone()
    cur = connection.cursor()
    cur.execute("UPDATE users_state SET game_counter = ?, total_score = ?, mean_score = ? WHERE tele_id = ?", (user_data[3] + 1, user_data[2] + score, round((user_data[2] + score) / (user_data[3] + 1),2) , tele_id, ))
    connection.commit()

    connection.close()


# connection = sqlite3.connect(DB_NAME)
# cur = connection.cursor()

# cur.execute("ALTER TABLE users_state ADD COLUMN mean_score")
# connection.commit()
# connection.close()
