"""MongoDB computes the summary; Python only submits and displays it."""
import argparse
import json
import os
from pymongo import MongoClient


def build_pipeline(start_year=1990, end_year=1999, min_votes=1000):
    if not (1800 <= start_year <= end_year <= 2100):
        raise ValueError("Choose an ordered year range from 1800 through 2100.")
    if min_votes < 0:
        raise ValueError("Minimum votes must be nonnegative.")
    return [
        {"$match": {"title_type": "movie", "start_year": {
            "$gte": start_year, "$lte": end_year}}},
        {"$lookup": {"from": "ratings", "localField": "_id",
                     "foreignField": "_id", "as": "rating"}},
        {"$unwind": "$rating"},
        {"$match": {"rating.num_votes": {"$gte": min_votes},
                    "rating.average_rating": {"$type": "number"}}},
        {"$group": {"_id": "$start_year", "rated_movies": {"$sum": 1},
                    "mean_rating": {"$avg": "$rating.average_rating"},
                    "total_votes": {"$sum": "$rating.num_votes"}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "year": "$_id", "rated_movies": 1,
                      "mean_rating": {"$round": ["$mean_rating", 2]},
                      "total_votes": 1}},
    ]


def connect():
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise RuntimeError("Set MONGODB_URI using the Chapter 16 connection steps.")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception:
        client.close()
        raise
    return client, client[os.environ.get("MONGODB_DATABASE", "imdb")]


def summarize(database, pipeline):
    # No $out or $merge: this pipeline does not modify the course data.
    return list(database.titles.aggregate(pipeline, maxTimeMS=30000, allowDiskUse=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize IMDb movie ratings by year")
    parser.add_argument("--start", type=int, default=1990)
    parser.add_argument("--end", type=int, default=1999)
    parser.add_argument("--min-votes", type=int, default=1000)
    args = parser.parse_args()
    pipeline = build_pipeline(args.start, args.end, args.min_votes)
    client, database = connect()
    try:
        print(json.dumps(summarize(database, pipeline), indent=2))
    finally:
        client.close()
