import json
from fastapi import Depends, FastAPI, HTTPException, Request, status, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import crud, models, helper, config
from .database import SessionLocal, engine
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="./templates/static"), name="static")
pth = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(pth, "..", "templates"))


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def read_user(username: str, db: Session):
    db_user = crud.get_user(db, username=username)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    return db_user


def check_authorized(token: str, db: Session):
    db_user = crud.get_user_by_token(db=db, token=token)
    if not db_user:
        return False

    return db_user.token == token


def invalidate_auth(token: str, db: Session):
    db_user = crud.get_user_by_token(db, token=token)
    if db_user:
        crud.update_user_token(db=db, username=db_user.username, token="")


@app.get('/login')
def login(request: Request, db: Session = Depends(get_db), referer=None):
    if helper.is_ip_local(request.client.host):
        # Local network user. Authorize.
        access_token = helper.generate_token()
        crud.update_user_token(db=db, username=config.LOCAL_USER_NAME, token=access_token)
        response = RedirectResponse(url=referer, status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="token", value=access_token)
        return response

    return templates.TemplateResponse("login.html", {"request": request, "referer": referer})


@app.post('/login')
def login(request: Request, data: OAuth2PasswordRequestForm = Depends(),  db: Session = Depends(get_db), referer="/"):
    username = data.username
    password = data.password

    if not helper.is_ip_local(request.client.host) and username == config.LOCAL_USER_NAME:
        raise HTTPException(status_code=400, detail="Local username is unacceptable for remote users.")

    user = read_user(username=username, db=db)
    if user is not None and helper.verify_password(plain_text_password=password, hashed_password=user.hashed_password):
        access_token = helper.generate_token()
        crud.update_user_token(db=db, username=user.username, token=access_token)

        user = read_user(username=username, db=db)

        response = RedirectResponse(url=referer, status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="token", value=user.token)

        return response
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")


@app.get("/logout")
def logout(token: str = Cookie(default=None), db: Session = Depends(get_db)):
    invalidate_auth(token=token, db=db)
    helper.stop_webcam_stream()
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    # return "You are logged out"


@app.get("/")
def home(request: Request, token: str = Cookie(default=None), db: Session = Depends(get_db), status_msg: str = ""):
    if not check_authorized(token=token, db=db):
        return RedirectResponse(url='/login?referer=/', status_code=status.HTTP_302_FOUND)

    helper.start_webcam_stream()

    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/printer_on")
def printer_on(token: str = Cookie(default=None), db: Session = Depends(get_db)):
    if not check_authorized(token=token, db=db):
        return RedirectResponse(url='/login?referer=/', status_code=status.HTTP_302_FOUND)

    helper.printer_power(turn_on=True)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@app.get("/printer_off")
def printer_off(token: str = Cookie(default=None), db: Session = Depends(get_db)):
    if not check_authorized(token=token, db=db):
        return RedirectResponse(url='/login?referer=/', status_code=status.HTTP_302_FOUND)

    helper.printer_power(turn_on=False)
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
