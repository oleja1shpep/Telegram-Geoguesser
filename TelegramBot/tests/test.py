from backend.database import MongoDB

def test_set_get_key():
    database = MongoDB()
    tele_id = "1234"
    key = "some_key"
    value = 42
    database.add_user(tele_id)
    database.set_key(tele_id, key, value)
    assert(database.get_key(tele_id, key, 0) == 42)
    database.delete_user(tele_id)

def test_get_key():
    database = MongoDB()
    tele_id = "1234"
    key = "some_key"
    value = 42
    database.add_user(tele_id)
    assert(database.get_key(tele_id, key, 42) == 42)
    database.delete_user(tele_id)