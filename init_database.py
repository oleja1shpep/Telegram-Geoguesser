import sqlite3

connection = sqlite3.connect("users.db")
cur = connection.cursor()

cur.execute("CREATE TABLE users_state(tele_id, total_scrore, game_counter)")

connection.commit()

connection.close()