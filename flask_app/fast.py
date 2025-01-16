from fastapi import FastAPI, APIRouter
from typing import Union
from pydantic import BaseModel

tags_metadata = [
    {"name": "users", "description": "Operations with users."},
    {"name": "items", "description": "Manage items."},
]

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

app = FastAPI(openapi_tags=tags_metadata)

api_v1 = APIRouter()
api_v2 = APIRouter()

@api_v1.get("/users/", tags=["users"])
async def get_users_v1():
    return [{"name": "Alice"}]

@api_v2.get("/users/", tags=["users"])
async def get_users_v2():
    return [{"name": "Bob"}]

@app.get("/")
def read_root(message):
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

app.include_router(api_v1, prefix="/v1")
app.include_router(api_v2, prefix="/v2")