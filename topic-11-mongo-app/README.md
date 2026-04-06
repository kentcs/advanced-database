# Topic 08: Mongita Flask CRUD App

This topic builds a Flask CRUD application on top of Mongita.

## Goals

- Keep the app close to the earlier SQL/ORM examples.
- Move all data access into `database.py`.
- Return document IDs as strings for URLs and convert them back to `ObjectId` values for queries.
- Enforce the same concepts from topic 05 manually in the data layer:
  - `pet.name`, `pet.type`, and `pet.owner_id` are required
  - `owner.name` is required
  - a pet must reference an existing owner
  - an owner cannot be deleted while pets still reference it
- Use `setup_database()` to initialize the collections on first run.

## Requirements

```bash
pip3 install -r requirements.txt
```

## Run

```bash
python3 app.py
```

## Notes

- This app uses two collections: `pets` and `owners`.
- The data layer returns `id` as a string.
- `create_pet`, `update_pet`, `delete_pet`, `create_owner`, `update_owner`, and `delete_owner` perform validation and raise errors when the input is invalid, missing, or violates a manual constraint.
