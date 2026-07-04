from fastapi import HTTPException, status
from pydantic import BaseModel
from app.config import settings

class User(BaseModel):
    username: str
    password: str

class AuthService:
    def __init__(self):
        self.users = {}

    async def user_exists(self, username: str) -> bool:
        return username in self.users

    async def register_user(self, user: User):
        if await self.user_exists(user.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
        self.users[user.username] = user.password
        return {"message": "User registered successfully"}

    async def login_user(self, user: User) -> str:
        if not await self.user_exists(user.username):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if self.users[user.username] != user.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return "dummy_token"
