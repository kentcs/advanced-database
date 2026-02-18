import sqlite3
from pprint import pprint

connection = None

def initialize(database_file):
    global connection
    connection = sqlite3.connect(database_file, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    print("succeeded in making connection.")

def get_pets():
    cursor = connection.cursor()
    cursor.execute("""select * from pet""")
    pets = cursor.fetchall()
    pets = [dict(pet) for pet in pets]
    for pet in pets:
        print(pet)
    return pets

def get_pet(id):
    id = int(id)
    cursor = connection.cursor()
    cursor.execute("""select * from pet where id = ?""", (id,))
    pets = cursor.fetchall()
    pets = [dict(pet) for pet in pets]
    assert len(pets) == 1
    if len(pets) == 0:
        return None
    return pets[0]

def create_pet(data):
    try:
        data["age"] = int(data["age"])
    except:
        data["age"] = 0
    cursor = connection.cursor()
    cursor.execute(
        """insert into pet(name, age, type, owner) values (?,?,?,?)""",
        (data["name"], data["age"], data["type"], data["owner"]),
    )
    connection.commit()

def delete_pet(id):
    id = int(id)
    cursor = connection.cursor()
    cursor.execute(f"""delete from pet where id = ?""", (id,))
    connection.commit()

def update_pet(id, data):
    try:
        data["age"] = int(data["age"])
    except:
        data["age"] = 0
    cursor = connection.cursor()
    cursor.execute(
        """update pet set name=?, age=?, type=?, owner=? where id=?""",
        (data["name"], data["age"], data["type"], data["owner"], id),
    )
    connection.commit()

def setup_test_database():
    initialize("test_pets.db")
    cursor = connection.cursor()
    cursor.execute("drop table if exists pet;")
    cursor.execute(
        """
        create table if not exists pet (
            id integer primary key autoincrement,
            name text not null,
            type text not null,
            age integer,
            owner text
        )
    """
    )
    connection.commit()
    pets = [
        {"name": "dorothy", "type": "dog", "age": 9, "owner": "greg"},
        {"name": "suzy", "type": "mouse", "age": 9, "owner": "greg"},
        {"name": "casey", "type": "dog", "age": 9, "owner": "greg"},
        {"name": "heidi", "type": "cat", "age": 15, "owner": "david"},
    ]
    for pet in pets:
        create_pet(pet)
    pets = get_pets()
    assert len(pets) == 4


def test_get_pets():
    print("testing get_pets()")
    pets = get_pets()
    assert type(pets) is list
    assert type(pets[0]) is dict
    for key in ["name","age"]:
        assert key in pets[0]
        assert type(pets[0]["name"]) == str 


def test_create_pet():
    print("testing get_pets()")
    pass


if __name__ == "__main__":
    setup_test_database()
    test_get_pets()
    test_create_pet()
    print("done.")

# initialize("pets.db")
# cursor = connection.execute("select * from pet")
# rows = [dict(row) for row in cursor.fetchall()]
# pprint(rows)

# These is a tuple
# ("a",1,"b",2)
# This is a dictionary
# { "name": "a","age":1,"kind":"b","whatever":2 }
