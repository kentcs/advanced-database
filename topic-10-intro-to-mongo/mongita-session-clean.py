# Mongita Interactive Session - MongoDB Concepts Introduction

# Installation:
# pip3 install mongita

# Import and connect
from mongita import MongitaClientDisk

client = MongitaClientDisk()

# Access database and collection (created automatically)
hello_world_db = client.hello_world_db
mongoose_collection = hello_world_db.mongoose_collection

# Insert documents
mongoose_collection.insert_many(
    [
        {"name": "Meercat", "does_not_eat": "Snakes"},
        {"name": "Yellow mongoose", "eats": "Termites"},
    ]
)

# Count documents
mongoose_collection.count_documents({})
# Returns: 2

# Update a document (add new field)
mongoose_collection.update_one({"name": "Meercat"}, {"$set": {"weight": 2}})

# Query with condition
cursor = mongoose_collection.find({"weight": {"$gt": 1}})
mongoose_list = list(cursor)
len(mongoose_list)
# Returns: 1

mongoose_list
# Returns: [{'name': 'Meercat', 'does_not_eat': 'Snakes', '_id': ObjectId('...'), 'weight': 2}]

# Find all documents
list(mongoose_collection.find())
# Returns both documents

# Find with query
list(mongoose_collection.find({"weight": {"$gt": 1}}))
# Returns: [{'name': 'Meercat', 'does_not_eat': 'Snakes', '_id': ObjectId('...'), 'weight': 2}]

# Delete a document
mongoose_collection.delete_one({"name": "Meercat"})

# Verify deletion
list(mongoose_collection.find({"weight": {"$gt": 1}}))
# Returns: []

# Insert again
mongoose_collection.insert_many([{"name": "Meercat", "does_not_eat": "Snakes"}])

# Check final state
list(mongoose_collection.find())
# Returns: [
#   {'name': 'Yellow mongoose', 'eats': 'Termites', '_id': ObjectId('...')},
#   {'name': 'Meercat', 'does_not_eat': 'Snakes', '_id': ObjectId('...')}
# ]
