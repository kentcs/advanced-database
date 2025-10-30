from pprint import pprint
import mongita

from mongita import MongitaClientDisk
from bson.objectid import ObjectId

client = MongitaClientDisk()

pets_db = client.pets_db

def get_pets():
    pet_collection = pets_db.pet_collection
    kind_collection = pets_db.kind_collection
    pets = list(pet_collection.find())
    for pet in pets:
        pet["id"] = str(pet["_id"])
        del pet["_id"]
        kind = kind_collection.find_one({"_id":pet["kind_id"]})
        for tag in ["kind_name","noise","food"]:
            pet[tag] = kind[tag]
        del pet["kind_id"]
        # pet["_id"] = ObjectId(pet["id"])
    return pets

def test_get_pets():
    print("test get_pets")
    pets = get_pets()
    assert type(pets) is list
    assert type(pets[0]) is dict
    assert type(pets[0]['id']) is str
    pets[0]['id'] = '1'
    assert pets[0] == {'id': '1', 'name': 'Suzy', 'age': 3, 'owner': 'Greg', 'kind_name': 'Dog', 'food': 'Dog food', 'noise': 'Bark'}

def get_pet(id):
    pet_collection = pets_db.pet_collection
    id = ObjectId(id)
    pet = pet_collection.find_one({"_id":id})
    pet["id"] = str(pet["_id"])
    del pet["_id"]
    return pet

def test_get_pet():
    print("test get_pet")
    pets = get_pets()
    id = pets[0]["id"]
    pet = get_pet(id)
    del pet["kind_id"]
    assert pet == {'id': id, 'name': 'Suzy', 'age': 3,  'owner': 'Greg'}  

def get_kinds():
    kind_collection = pets_db.kind_collection
    kinds = list(kind_collection.find())
    for kind in kinds:
        kind["id"] = str(kind["_id"])
        del kind["_id"]

    return kinds

def test_get_kinds():
    print("test get_kinds")
    kinds = get_kinds()    
    assert type(kinds) is list
    assert type(kinds[0]) is dict
    assert type(kinds[0]['id']) is str
    kind = kinds[0]
    assert kind["kind_name"] == "Dog"
    assert kind["food"] == "Dog food"
    assert kind["noise"] == "Bark"

def get_kind(id):
    kind_collection = pets_db.kind_collection
    id = ObjectId(id)
    kind = kind_collection.find_one({"_id":id})
    kind["id"] = str(kind["_id"])
    del kind["_id"]
    return kind

def test_get_kind():
    print("test get_kind")
    kinds = get_kinds()
    id = kinds[0]["id"]
    kind = get_kind(id)
    assert kind["id"] == id
    assert kind["kind_name"] == "Dog"
    assert kind["food"] == "Dog food"
    assert kind["noise"] == "Bark"

def create_pet(data):
    try:
        data["age"] = int(data["age"])
    except:
        data["age"] = 0
    # pets_collection = pets_db.pets_collection # <- Wrong table name
    pet_collection = pets_db.pet_collection
    # pets_collection.insert_one(data)
    pet_collection.insert_one(data)
    print(list(pet_collection.find())) # <- Debug Print
    

def test_create_pet():
    kinds = get_kinds()
    #print(kinds)
    #exit(0)
    #id = None
    for kind in kinds:
        if kind["kind_name"] == "Dog":
            kind_id = kind["id"]
    assert kind_id != None
    assert type(kind_id) == str
    data = {
        "name": "Lassie",
        "age":8,
        "kind_id": kind_id,
        "owner":"Bobby"
    }
    create_pet(data)
    pets = get_pets()
    #print(pets)
    for pet in pets:
        if pet["name"] == "Lassie":
            print(pet) # <- Debug print
            assert type(pet["id"]) == str
            assert pet["owner"] == "Bobby"
            # assert pet["kind_id"] == kind_id 
            # Whenever get_pets() is called, pet["kind_id"] is replaced by pet["kind_name"]
            assert pet["kind_name"] == "Dog"
            return
    raise Exception("Created pet not found")    




#========================
# def create_pet(data):
#     try:
#         data["age"] = int(data["age"])
#     except:
#         data["age"] = 0
#     cursor = connection.cursor()
#     cursor.execute(
#         """insert into pet(name, age, kind_id, owner) values (?,?,?,?)""",
#         (data["name"], data["age"], data["kind_id"], data["owner"]),
#     )
#     connection.commit()

# def create_kind(data):
#     cursor = connection.cursor()
#     cursor.execute(
#         """insert into kind(name, food, sound) values (?,?,?)""",
#         (data["name"], data["food"], data["sound"]),
#     )
#     connection.commit()

# def test_create_pet():
#     pass


# def update_pet(id, data):
#     try:
#         data["age"] = int(data["age"])
#     except:
#         data["age"] = 0
#     cursor = connection.cursor()
#     cursor.execute(
#         """update pet set name=?, age=?, type=?, owner=? where id=?""",
#         (data["name"], data["age"], data["type"], data["owner"], id),
#     )
#     connection.commit()

# def update_kind(id, data):
#     cursor = connection.cursor()
#     cursor.execute(
#         """update kind set name=?, food=?, sound=? where id=?""",
#         (data["name"], data["food"], data["sound"], id),
#     )
#     connection.commit()

# def delete_pet(id):
#     cursor = connection.cursor()
#     cursor.execute(f"""delete from pet where id = ?""", (id,))
#     connection.commit()

# def delete_kind(id):
#     cursor = connection.cursor()
#     cursor.execute(f"""delete from kind where id = ?""", (id,))
#     connection.commit()
#========================  

def create_sample_database():
    print("create sample database...")
    global client
    client = MongitaClientDisk(host="./sample_database")
    pets_db = client.pets_db
    pets_db.drop_collection("kind_collection")
    kind_collection = pets_db.kind_collection
    kind_collection.insert_many([
        {
            "kind_name":'Dog', 
            "food":'Dog food', 
            "noise":'Bark'
        },
        {
            "kind_name":'Cat', 
            "food":'Cat food', 
            "noise":'Meow'
        },
        {
            "kind_name":'Fish', 
            "food":'Fish flakes', 
            "noise":'Blub'
        }
    ])
    kinds = list(kind_collection.find())
    pets_db.drop_collection("pet_collection")
    pet_collection = pets_db.pet_collection
    pets = [
        {'name':'Suzy', 'age':3, "kind_name":"Dog", 'owner':'Greg'},
        {'name':'Sandy', 'age':2, "kind_name":"Cat", 'owner':'Steve'},
        {'name':'Dorothy', 'age':1, "kind_name":"Dog", 'owner':'Elizabeth'},
        {'name':'Heidi', 'age':4, "kind_name":"Dog",'owner':'David'}
    ]
    for pet in pets:
        for kind in kinds:
            if kind["kind_name"] == pet["kind_name"]:
                pet["kind_id"] = kind["_id"]
        del pet["kind_name"]
        assert "kind_id" in pet.keys()

    pet_collection.insert_many(pets)


if __name__ == "__main__":
    create_sample_database()
    pets_db = client.pets_db # cannot initiate sample data without this line
    test_get_pets()
    test_get_pet()
    test_get_kinds()
    test_get_kind()
    test_create_pet()
