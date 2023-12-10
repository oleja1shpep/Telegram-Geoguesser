import sqlite3

connection = sqlite3.connect("users.db")
cur = connection.cursor()

cur.execute("CREATE TABLE users_state(tele_id, username, total_score, game_counter)")

connection.commit()

connection.close()