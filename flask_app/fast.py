from fastapi import FastAPI, APIRouter

tags_metadata = [
    {"name": "users", "description": "Operations with users."},
    {"name": "items", "description": "Manage items."},
]

app = FastAPI(openapi_tags=tags_metadata)

api_v1 = APIRouter()
api_v2 = APIRouter()

@api_v1.get("/users/", tags=["users"])
async def get_users_v1():
    return [{"name": "Alice"}]

@api_v2.get("/users/", tags=["users"])
async def get_users_v2():
    return [{"name": "Bob"}]

app.include_router(api_v1, prefix="/v1")
app.include_router(api_v2, prefix="/v2")