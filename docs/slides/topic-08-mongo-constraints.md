# Topic 08: Mongo Constraints

Topic 05 used SQLite constraints. Topic 08 keeps the same rules, but enforces them in application code.

---

## Topic 05 Constraints

- `pet.name` is required
- `pet.type` is required
- `pet.owner_id` is required
- `owner.name` is required
- `pet.owner_id` must reference an existing owner
- an owner with pets cannot be deleted

SQLite enforced most of this with schema and foreign keys.

---

## Topic 08 Data Model

- two collections: `pets` and `owners`
- document IDs are `ObjectId` values
- the data layer returns IDs as strings
- route code converts strings back to `ObjectId` when querying

Mongo does not give us the same relational constraints for free.

---

## Manual Enforcement

In `database.py` we validate before writing:

```python
_require_text(data.get("name"), "name")
_require_text(data.get("type"), "type")
_require_owner(data.get("owner_id"))
```

This replaces `NOT NULL` and foreign-key checks.

---

## Pet Validation

```python
def _normalize_pet_data(data):
    owner_id = data.get("owner_id")
    if (owner_id or "").strip() == "":
        raise ValueError("owner_id is required.")

    return {
        "name": _require_text(data.get("name"), "name"),
        "type": _require_text(data.get("type"), "type"),
        "age": _normalize_age(data.get("age")),
        "owner_id": _require_owner(owner_id),
    }
```

This is the topic 05 `NOT NULL` and FK logic, written in Python.

---

## Owner Validation

```python
def _normalize_owner_data(data):
    return {
        "name": _require_text(data.get("name"), "name"),
        "city": (data.get("city") or "").strip() or None,
        "type_of_home": (data.get("type_of_home") or "").strip() or None,
    }
```

Here we only require `name`. The other fields are optional.

---

## Owner Rules

- `create_owner()` requires a name
- `update_owner()` requires a valid owner ID
- `delete_owner()` checks whether pets still reference that owner

If pets exist, the delete raises a constraint error.

---

## Delete Restriction

```python
def delete_owner(id):
    object_id, _ = _require_existing_owner(id)
    pet = pets_collection.find_one({"owner_id": object_id})
    if pet is not None:
        raise ConstraintError(
            "Cannot delete this owner because they have pets. Please delete their pets first."
        )

    owners_collection.delete_one({"_id": object_id})
```

That is the Mongo version of `ON DELETE RESTRICT`.

---

## Pet Rules

- `create_pet()` requires `name`, `type`, and `owner_id`
- the owner must exist before the pet can be saved
- `update_pet()` re-checks the same rules
- `delete_pet()` fails if the pet ID is missing or invalid

This is topic 05 behavior, but implemented in code instead of SQL.

---

## ID Conversion

```python
def pet_to_dict(pet):
    return {
        "id": str(pet["_id"]),
        "name": pet["name"],
        "type": pet["type"],
        "age": pet["age"],
        "owner_id": str(pet["owner_id"]),
    }
```

```python
def _to_object_id(value, field_name="id"):
    try:
        return ObjectId(str(value))
    except Exception as exc:
        raise ValueError(f"{field_name} must be a valid ObjectId string.") from exc
```

Return strings to the web layer. Convert back to `ObjectId` before querying.

---

## Mongo Advice

- validate early in the data layer
- keep ID conversion at the boundary
- raise clear errors for missing or invalid references
- treat app code as the constraint engine
- add tests for both success and failure paths

Mongo is flexible, so your code has to be explicit.

---

## Key Takeaways

- topic 05 relied on database constraints
- topic 08 relies on manual constraint logic
- the user-facing behavior should still feel the same
- tests should prove both the happy path and the blocked path
