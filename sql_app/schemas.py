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


class GeneralDataBase(BaseModel):
    data_key: str


class GeneralDataCreate(GeneralDataBase):
    data_value: str


class GeneralData(GeneralDataBase):
    id: int
    data_key: str
    data_value: str
    timestamp: int

    class Config:
        orm_mode = True