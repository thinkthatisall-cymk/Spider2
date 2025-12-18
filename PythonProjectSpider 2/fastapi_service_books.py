from http import HTTPStatus
from os import getenv
from typing import Any, Mapping

from fastapi import FastAPI, HTTPException
import pymongo


app = FastAPI(title="Book ISBN Search Service", description="Study Case Example")


def get_collection() -> pymongo.collection.Collection[Mapping[str, Any] | Any]:
    mongo_user = getenv("MONGO_USER", "books_user")
    mongo_password = getenv("MONGO_PASSWORD", "books_pass")
    mongo_host = getenv("MONGO_HOST", "localhost")
    mongo_port = getenv("MONGO_PORT", "27017")

    mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"

    mongo_db = getenv("MONGO_DATABASE", "items")
    mongo_db_collection = getenv("MONGO_DATABASE_COLLECTION", "scraped_books")

    client = pymongo.MongoClient(mongo_uri)
    db = client[mongo_db]
    return db[mongo_db_collection]


@app.get("/search_by_isbn", tags=["ISBN Searcher"])
def get_book_by_isbn(isbn: str) -> dict:
    collection = get_collection()
    result = collection.find_one({"isbn": isbn}, {"_id": 0})
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Can't find book with this ISBN",
        )
    # Просто возвращаем словарь как есть, без Pydantic-модели
    return result


