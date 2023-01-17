from sqlalchemy.orm import Session

from . import models, schemas
from .helper import *
import time
from .config import TOKEN_DURATION


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_token(db: Session, token: str):
    return db.query(models.User).filter(models.User.token == token).first()


def update_user_token(db: Session, username: str, token: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    user.token = token
    user.token_expire_time = time.time() + TOKEN_DURATION
    db.commit()
