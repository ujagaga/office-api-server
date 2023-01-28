from sqlalchemy.orm import Session

from . import models, config, schemas
import time


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_token(db: Session, token: str):
    return db.query(models.User).filter(models.User.token == token).first()


def update_user_token(db: Session, username: str, token: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    user.token = token
    user.token_expire_time = time.time() + config.TOKEN_DURATION
    db.commit()


def get_general_data(db: Session, data_key: str):
    return db.query(models.GeneralData).filter(models.GeneralData.data_key == data_key).first()


def create_general_data(db: Session, data_key: str, data_value: str):
    data = models.GeneralData(data_key=data_key, data_value=data_value, timestamp=int(time.time()))
    db.add(data)
    db.commit()
    db.refresh(data)


def set_general_data(db: Session, data_key: str, data_value: str):
    data = db.query(models.GeneralData).filter(models.GeneralData.data_key == data_key).first()
    if not data:
        create_general_data(db=db, data_key=data_key, data_value=data_value)
    else:
        data.data_key = data_key
        data.data_value = data_value
        data.timestamp = int(time.time())
        db.commit()
