import os

from peewee import IntegerField, Model, SqliteDatabase, TextField

database = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = database

class Pet(BaseModel):
    name = TextField(null=False)
    type = TextField(null=False)
    age = IntegerField(default=0)

def initialize(database_file):
    if not database.is_closed():
        database.close()
    database.init(database_file)
    database.connect(reuse_if_open=True)
    database.create_tables([Pet])

def close_connection():
    if not database.is_closed():
        database.close()

def _normalize_age(value):
    try:
        return int(value)
    except Exception:
        return 0

def pet_to_dict(pet):
    return {"id": pet.id, "name": pet.name, "type": pet.type, "age": pet.age}


def get_pets():
    query = Pet.select().order_by(Pet.name)
    return [pet_to_dict(pet) for pet in query]

def get_pet(id):
    pet = Pet.get_or_none(Pet.id == int(id))
    if pet is None:
        return None
    return pet_to_dict(pet)

def create_pet(data):
    if "name" not in data:
        raise Exception("Hey! Pet doesn't have name.")
    if data["name"].strip()=="":
        raise Exception("Hey! Pet doesn't have name.")
    pet = Pet.create(
        name=(data.get("name") or "").strip(),
        type=(data.get("type") or "").strip(),
        age=_normalize_age(data.get("age")),
    )
    return pet.id

def delete_pet(id):
    Pet.delete().where(Pet.id == int(id)).execute()


def update_pet(id, data):
    if "name" not in data:
        raise Exception("Hey! Pet doesn't have name.")
    if data["name"].strip()=="":
        raise Exception("Hey! Pet doesn't have name.")
    Pet.update(
        name=(data.get("name") or "").strip(),
        type=(data.get("type") or "").strip(),
        age=_normalize_age(data.get("age")),
    ).where(Pet.id == int(id)).execute()

def setup_test_database(db_file="test_pets.db"):
    close_connection()
    try:
        os.remove(db_file)
    except FileNotFoundError:
        pass

    initialize(db_file)

    pets = [
        {"name": "dorothy", "type": "dog", "age": 9},
        {"name": "suzy", "type": "mouse", "age": 9},
        {"name": "casey", "type": "dog", "age": 9},
        {"name": "heidi", "type": "cat", "age": 15},
    ]
    for pet in pets:
        create_pet(pet)

    assert len(get_pets()) == 4


def test_get_pets():
    pets = get_pets()
    assert type(pets) is list
    assert len(pets) >= 1
    assert type(pets[0]) is dict
    for key in ["id", "name", "type", "age"]:
        assert key in pets[0]
    assert type(pets[0]["name"]) is str


def test_create_pet_and_get_pet():
    new_id = create_pet({"name": "walter", "age": "2", "type": "mouse"})
    pet = get_pet(new_id)
    assert pet is not None
    assert pet["name"] == "walter"
    assert pet["age"] == 2
    assert pet["type"] == "mouse"


def test_update_pet():
    new_id = create_pet({"name": "temp", "age": 1, "type": "cat"})
    update_pet(new_id, {"name": "updated", "age": "8", "type": "dog"})
    pet = get_pet(new_id)
    assert pet is not None
    assert pet["name"] == "updated"
    assert pet["age"] == 8
    assert pet["type"] == "dog"


def test_delete_pet():
    new_id = create_pet({"name": "delete_me", "age": 3, "type": "fish"})
    delete_pet(new_id)
    assert get_pet(new_id) is None


if __name__ == "__main__":
    setup_test_database()
    test_get_pets()
    test_create_pet_and_get_pet()
    test_update_pet()
    test_delete_pet()
    close_connection()
    print("done.")
