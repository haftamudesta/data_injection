from fastapi import FastAPI, Depends, Header, Path, HTTPException, status
from typing import Annotated
from pydantic import BaseModel

app = FastAPI()

class CreateItem(BaseModel):
    name: str
    price: float | None = None

async def get_db_session():
    print("DB session started..")
    session = {"data": {1: {"name": "Item One"}, 2: {"name": "Item two"}, 3: {"name": "Item three"}}}
    try:
        yield session
    finally:
        print("Db session teardown...")

DbSession = Annotated[dict, Depends(get_db_session)]
async def get_user(token: Annotated[str | None, Header()] = None):
    print("Checking Auth...")
    user = {"username": "test user"}  # Changed "userName" to "username" (lowercase)
    return user

CurrentUser = Annotated[dict, Depends(get_user)]
@app.post("/item")
async def createItem(
    item: CreateItem,
    db: DbSession,
    user: CurrentUser):  
    print(f"user {user['username']} creating item")
    new_id = max(db["data"].keys() or [0]) + 1
    db["data"][new_id] = item.model_dump()
    return {"id": new_id, **item.model_dump()}
@app.get("/item/{item_id}")
async def read_items(item_id: Annotated[int, Path(ge=1)], db: DbSession):
    print("Reading Item")
    if item_id not in db["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Item with id({item_id}) not found" 
        )
    return {"id": item_id, **db["data"][item_id]}
@app.get("/")
async def root():
    return {"message": "FastAPI app is running"}