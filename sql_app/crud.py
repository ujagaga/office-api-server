from sqlalchemy.orm import Session

from . import models, config
import time


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_token(db: Session, token: str):
    return db.query(models.User).filter(models.User.token == token).first()


def create_local_user(db: Session):
    user = models.User(username=config.LOCAL_USER_NAME, hashed_password="local_pass123", email="local@officeserver.local")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_token(db: Session, username: str, token: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if username == config.LOCAL_USER_NAME and user is None:
        user = create_local_user(db=db)
    user.token = token
    user.token_expire_time = time.time() + config.TOKEN_DURATION
    db.commit()

