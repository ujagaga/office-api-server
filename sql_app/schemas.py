from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    username: str
    token: str
    token_expire_time: int
    hashed_password: str

    class Config:
        orm_mode = True
