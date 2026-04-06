# Topic 07: Intro to Mongo and Mongita

We begin with Mongita so we can learn document-database ideas locally before moving to full Mongo deployments.

---

## Topic Goals

- Understand document-oriented data
- Compare relational tables to document collections
- Start with Mongita as a local Mongo-like datastore
- Perform basic CRUD with a Mongo-style API
- Prepare for Mongo, Mongo Atlas, and larger deployments later

---

## Why Move Beyond Relational Only?

Relational databases are strong when:
- structure is fixed
- joins are central
- integrity constraints are strict

Document databases are useful when:
- records vary in shape
- nested data is common
- rapid iteration matters

---

## Mental Model Shift

Relational model:
- database
- tables
- rows
- columns

Document model:
- database
- collections
- documents
- fields

---

## A Pet Record in SQL Thinking

```text
pets
id | name | age | owner | kind_id
```

Related data often lives in separate tables and is joined later.

---

## A Pet Record in Document Thinking

```json
{
  "name": "Suzy",
  "age": 3,
  "owner": "Greg",
  "kind": {
    "name": "dog",
    "food": "kibble"
  }
}
```

Data that belongs together can often live together.

---

## Why Start with Mongita?

- Runs locally with no Mongo server setup
- Uses a familiar Mongo-style API
- Good for classroom experimentation
- Lets us focus on documents, collections, and queries first

Mongita is a teaching bridge, not a production replacement for MongoDB.

---

## Install

```bash
pip install mongita
```

The package gives you an embedded, local document store.

---

## First Connection

```python
from mongita import MongitaClientDisk

client = MongitaClientDisk()
db = client["pets_db"]
collection = db["pets"]
```

This creates or opens a local on-disk Mongita database.

---

## Insert One Document

```python
collection.insert_one({
    "name": "Suzy",
    "age": 3,
    "owner": "Greg",
    "kind": "dog",
})
```

Mongo-style inserts accept Python dictionaries.

---

## Insert Many Documents

```python
collection.insert_many([
    {"name": "Milo", "age": 2, "owner": "Ava", "kind": "cat"},
    {"name": "Rex", "age": 5, "owner": "Sam", "kind": "dog"},
])
```

Collections do not require every document to have exactly the same fields.

---

## Read Documents

```python
for pet in collection.find():
    print(pet)
```

`find()` returns matching documents, similar to a query cursor.

---

## Filter Documents

```python
dogs = collection.find({"kind": "dog"})

for dog in dogs:
    print(dog["name"])
```

The filter is expressed as a dictionary.

---

## Find One

```python
pet = collection.find_one({"name": "Suzy"})
print(pet)
```

`find_one()` is often the easiest entry point for simple lookups.

---

## Update a Document

```python
collection.update_one(
    {"name": "Suzy"},
    {"$set": {"age": 4}}
)
```

Mongo-style update operators modify matching documents.

---

## Delete a Document

```python
collection.delete_one({"name": "Rex"})
```

Deletion filters work the same way as read filters.

---

## Document IDs

Mongo-style systems usually attach an `_id` field.

```python
pet = collection.find_one({"name": "Suzy"})
print(pet["_id"])
```

This acts as the primary identifier for the document.

---

## Flexible Schema

These can coexist in the same collection:

```python
{"name": "Suzy", "kind": "dog"}
{"name": "Milo", "kind": "cat", "favorite_toy": "mouse"}
```

That flexibility is powerful, but it also shifts responsibility to application logic.

---

## Tradeoffs of Flexible Documents

Benefits:
- fast iteration
- fewer migrations early on
- natural nested data

Costs:
- weaker structure guarantees
- inconsistent fields if teams are careless
- validation becomes more important

---

## Embedding vs Referencing

Embedding:
- store related data inside the document
- good for tightly coupled data

Referencing:
- store IDs that point elsewhere
- better when related data changes independently

This is one of the big design choices in document databases.

---

## Example: Embedded Owner Info

```json
{
  "name": "Suzy",
  "kind": "dog",
  "owner": {
    "name": "Greg",
    "city": "Canton"
  }
}
```

Convenient to read, but repeated owner data may drift over time.

---

## SQL vs Mongita Summary

SQL:
- fixed schema first
- joins are normal
- normalization is central

Mongita / Mongo:
- document shape can evolve
- nesting is common
- denormalization is often acceptable

---

## Practical Classroom Workflow

1. Start with Mongita locally
2. Learn collections, documents, filters, and updates
3. Practice data modeling decisions
4. Move to Mongo server or Atlas later

That sequence reduces setup friction while preserving the core ideas.

---

## Topic 07 Summary

- Mongita gives us a local Mongo-like environment
- Document databases organize data as collections of documents
- CRUD uses a dictionary-based query style
- Flexible schema is useful, but requires discipline
- Today is about concepts first, infrastructure later
