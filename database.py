import sqlite3


def search_tele_id(tele_id):
    connection = sqlite3.connect("users.db")
    cur = connection.cursor()
    
    find_login = cur.execute("SELECT tele_id FROM users_state WHERE tele_id = ?", (tele_id, ))
    if (find_login.fetchone() == None):
        cur.execute("""INSERT INTO users_state VALUES
                    (?, 0, 0)
                    """, (tele_id, ))
        connection.commit()
        connection.close()
        return False
    
    return True
        