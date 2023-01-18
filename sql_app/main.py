import json

from fastapi import Depends, FastAPI, HTTPException, Request, status, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import crud, models, helper, config
from .database import SessionLocal, engine
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="./templates/static"), name="static")
pth = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(pth, "..", "templates"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get('/api')
def api_root(token: str = "", db: Session = Depends(get_db)):
    if token is None:
        return {"Status": "ERROR", "Detail": "Token missing. Please login."}

    if not check_authorized(token=token, db=db):
        return {"Status": "ERROR", "Detail": "Unauthorized. Please login."}

    return {"Status": "OK", "Detail": token}


@app.get('/api/auth')
def api_auth(username: str, password: str, db: Session = Depends(get_db)):
    user = read_user(username=username, db=db)

    if helper.verify_password(plain_text_password=password, hashed_password=user.hashed_password):
        token = helper.generate_token()
        user.token = token
        crud.update_user_token(db=db, username=user.username, token=token)

        # Update user to make sure token is set
        user = read_user(username=username, db=db)

        return {"Status": "OK", "Detail": "Login successful", "token:": user.token}
    else:
        return {"Status": "Error", "Detail": "Invalid password"}


@app.get('/api/mqtt')
def api_mqtt(token: str = "", db: Session = Depends(get_db), topic="", mqtt_msg=""):

    if token is None:
        status = "ERROR"
        detail = "Token missing. Please login."
    elif not check_authorized(token=token, db=db):
        status = "ERROR"
        detail = "Unauthorized. Please login."
    else:
        detail = helper.mqtt_publish(topic=topic, message=mqtt_msg)
        if "ERROR" in detail:
            status = "ERROR"
        else:
            status = "OK"

    return {"Status": status, "Detail": detail}


@app.get('/api/office_light_get')
def api_office_light_get(token: str = "", db: Session = Depends(get_db)):

    if token is None:
        status = "ERROR"
        detail = "Token missing. Please login."
    elif not check_authorized(token=token, db=db):
        status = "ERROR"
        detail = "Unauthorized. Please login."
    else:
        url = config.OFFICE_LIGHT_URL + "/api/status"
        response = helper.http_get_query(url)
        try:
            detail = json.loads(response)
        except:
            detail = response
        status = "OK"

    return {"Status": status, "Detail": detail}


@app.get('/api/office_light_set')
def api_office_light_set(token: str = "", db: Session = Depends(get_db), current=""):
    if token is None:
        status = "ERROR"
        detail = "Token missing. Please login."
    elif not check_authorized(token=token, db=db):
        status = "ERROR"
        detail = "Unauthorized. Please login."
    else:
        url = config.OFFICE_LIGHT_URL + f"/api/set?CURRENT={current}"
        detail = helper.http_get_query(url)
        status = "OK"

    return {"Status": status, "Detail": detail}


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
def logout(token: str | None = Cookie(default=None), db: Session = Depends(get_db)):
    invalidate_auth(token=token, db=db)
    return RedirectResponse(url='/?status_msg=status_msg="You are logged out"', status_code=status.HTTP_302_FOUND)
    # return "You are logged out"


@app.get("/")
def home(request: Request, token: str | None = Cookie(default=None), db: Session = Depends(get_db), status_msg: str=""):
    if not check_authorized(token=token, db=db):
        return RedirectResponse(url='/login?referer=/', status_code=status.HTTP_302_FOUND)

    helper.stop_webcam_stream()
    stream_result = helper.start_webcam_stream(token)
    if stream_result > 0:
        if len(status_msg) > 0:
            status_msg = f"{status_msg}, "
        status_msg = f"{status_msg}ERROR: Failed to start video streamer service. ({stream_result})"

    return templates.TemplateResponse("home.html", {
        "request": request, "status_msg": status_msg, "stream_user": config.USTREAMER_USER, "stream_pwd": token
    })


@app.get("/unlock_office")
def unlock_office(request: Request, token: str | None = Cookie(default=None), db: Session = Depends(get_db)):
    if not check_authorized(token=token, db=db):
        return RedirectResponse(url='/login?referer=/unlock_office', status_code=status.HTTP_302_FOUND)

    response = helper.http_get_query(url=config.UNLOCK_OFFICE_URL, params=config.UNLOCK_OFFICE_PARAMS)
    return RedirectResponse(url=f'/?status_msg={response}', status_code=status.HTTP_302_FOUND)


@app.get("/unlock_building")
def unlock_building(request: Request, token: str | None = Cookie(default=None), db: Session = Depends(get_db)):
    if not check_authorized(token=token, db=db):
        return RedirectResponse(url='/login?referer=/unlock_building', status_code=status.HTTP_302_FOUND)

    response = helper.mqtt_publish(topic=config.MQTT_INTERCOM_TOPIC, message="Unlock")
    return RedirectResponse(url=f'/?status_msg={response}', status_code=status.HTTP_302_FOUND)

