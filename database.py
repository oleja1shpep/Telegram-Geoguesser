import sqlite3


def search_tele_id(tele_id, tele_username):
    connection = sqlite3.connect("users.db")
    cur = connection.cursor()
    
    find_login = cur.execute("SELECT tele_id FROM users_state WHERE tele_id = ?", (tele_id, ))
    if (find_login.fetchone() == None):
        cur.execute("""INSERT INTO users_state VALUES
                    (?, ?, 0, 0)
                    """, (tele_id, tele_username, ))
        connection.commit()
        connection.close()
        return False
    connection.close()
    return True


def get_top10():
    connection = sqlite3.connect("users.db")
    cur = connection.cursor()
    rows = cur.execute("SELECT username, total_score, game_counter FROM users_state ORDER BY total_score")
    res = rows.fetchmany(10)
    connection.close()
    return res


