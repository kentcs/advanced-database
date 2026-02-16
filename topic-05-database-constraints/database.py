import sqlite3
from pprint import pprint

connection = None

def initialize(database_file):
    global connection
    connection = sqlite3.connect(database_file, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    print("succeeded in making connection.")

def get_owners():
    cursor = connection.cursor()
    cursor.execute("""select * from owner""")
    owners = cursor.fetchall()
    owners = [dict(owner) for owner in owners]
    #for owner in owners:
    #    print(owner)
    return owners

def get_owner(id):
    id = int(id)
    cursor = connection.cursor()
    cursor.execute("""select * from owner where id = ?""", (id,))
    owners = cursor.fetchall()
    owners = [dict(owner) for owner in owners]
    assert len(owners) == 1
    if len(owners) == 0:
        return None
    return owners[0]

def create_owner(data):
    cursor = connection.cursor()
    cursor.execute(
        """insert into owner(name, city, type_of_home) values (?,?,?)""",
        (data["name"], data.get("city"), data.get("type_of_home")),
    )
    connection.commit()

def delete_owner(id):
    id = int(id)
    cursor = connection.cursor()
    cursor.execute("""delete from owner where id = ?""", (id,))
    connection.commit()

def update_owner(id, data):
    cursor = connection.cursor()
    cursor.execute(
        """update owner set name=?, city=?, type_of_home=? where id=?""",
        (data["name"], data.get("city"), data.get("type_of_home"), id),
    )
    connection.commit()


def get_pets():
    cursor = connection.cursor()
    cursor.execute("""select * from pet""")
    pets = cursor.fetchall()
    pets = [dict(pet) for pet in pets]
    # for pet in pets:
    #     print(pet)
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
        """insert into pet(name, age, type, owner_id) values (?,?,?,?)""",
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
        """update pet set name=?, age=?, type=?, owner_id=? where id=?""",
        (data["name"], data["age"], data["type"], data["owner_id"], id),
    )
    connection.commit()

def setup_test_database():
    print("execute setup_database()")
    initialize("test_pets.db")
    cursor = connection.cursor()
    cursor.execute("drop table if exists pet;")
    cursor.execute("drop table if exists owner;")
    cursor.execute(
        """
        create table if not exists owner (
            id integer primary key autoincrement,
            name text not null,
            city text,
            type_of_home text
        )
    """
    )
    cursor.execute(
        """
        create table if not exists pet (
            id integer primary key autoincrement,
            name text not null,
            type text not null,
            age integer,
            owner_id integer not null, 
            foreign key (owner_id) references owner(id) on delete restrict
        )
    """
    )
    connection.commit()

    owners = [
        {"name": "greg", "city": "Portland", "type_of_home": "condo"},
        {"name": "david", "city": "Seattle", "type_of_home": "farm"},
    ]
    owner_ids = {}
    for owner in owners:
        cursor.execute(
            """insert into owner(name, city, type_of_home) values (?,?,?)""",
            (owner["name"], owner["city"], owner["type_of_home"]),
        )
        owner_ids[owner["name"]] = cursor.lastrowid
    connection.commit()

    pets = [
        {"name": "dorothy", "type": "dog", "age": 9, "owner": "greg"},
        {"name": "suzy", "type": "mouse", "age": 9, "owner": "greg"},
        {"name": "casey", "type": "dog", "age": 9, "owner": "greg"},
        {"name": "heidi", "type": "cat", "age": 15, "owner": "david"},
    ]
    for pet in pets:
        pet["owner_id"] = owner_ids[pet["owner"]]
        cursor.execute(
            """insert into pet(name, age, type, owner_id) values (?,?,?,?)""",
            (pet["name"], pet["age"], pet["type"], pet["owner_id"]),
        )
    connection.commit()
    pets = get_pets()
    assert len(pets) == 4

def test_get_owners():
    print("test get_owners()")
    owners = get_owners()
    assert type(owners) is list
    assert type(owners[0]) is dict
    for key in ["name","city","type_of_home"]:
        assert key in owners[0]
        assert type(owners[0]["name"]) == str 
        assert type(owners[0]["type_of_home"]) == str 

def test_get_owner():
    print("test get_owner()")
    owner = get_owner(2)
    assert owner["name"] == "david"

def test_create_owner():
    print("test create_owner()")
    create_owner({
        "name":"santa",
        "city":"north pole",
        "type_of_home":"workshop"
    })
    owners = get_owners()
    owners = [owner for owner in owners if owner["name"] == "santa"]
    owner = owners[0]
    assert owner["name"] == "santa"
    assert owner["city"] == "north pole"
    assert owner["type_of_home"] == "workshop"

def test_update_owner():
    print("test update_owner()")
    owners = get_owners()
    owner = [owner for owner in owners if owner["name"] == "david"][0]
    owner["name"] = "dave"
    owner["city"] = "riverside"
    owner["type_of_home"] = "suburban"
    id = owner["id"]
    update_owner(id, owner)
    owners = get_owners()
    owners = [owner for owner in owners if owner["name"] == "dave"][0]
    assert owner["id"] == id
    assert owner["name"] == "dave"
    assert owner["city"] == "riverside"
    assert owner["type_of_home"] == "suburban"

def test_delete_owner():
    print("test delete_owner()")
    owners = get_owners()
    owner = [owner for owner in owners if owner["name"] == "santa"][0]
    id = owner["id"]
    delete_owner(id)
    owners = get_owners()
    owners = [owner for owner in owners if owner["name"] == "santa"]
    assert owners == []

def test_get_pets():
    print("testing get_pets()")
    pets = get_pets()
    assert type(pets) is list
    assert type(pets[0]) is dict
    for key in ["name","age"]:
        assert key in pets[0]
    assert type(pets[0]["name"]) == str 
    assert type(pets[0]["type"]) == str 
    assert type(pets[0]["owner_id"]) == int


def test_create_pet():
    print("testing get_pets()")
    pass

def test_delete_owner_with_constraint():
    print("testing delete_owner() with constraint")
    pets = get_pets()
    pets = [pet for pet in pets if pet["owner_id"] == 1]
    assert len(pets) > 0
    try:
        delete_owner(1)
        assert False, "We have deleted an owner who has a pet!"
    except Exception as e:
        print(str(e))
        exit(0)


if __name__ == "__main__":
    setup_test_database()
    test_get_owners()
    test_get_owner()
    test_create_owner()
    test_update_owner()
    test_delete_owner()
    test_get_pets()
    test_create_pet()
    test_delete_owner_with_constraint()
    print("done.")

