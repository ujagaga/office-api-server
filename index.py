#!/usr/bin/env python3 
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, request, flash, g
import config
import database
import helper
import functools
import time

app = Flask(__name__)

app.config["SECRET_KEY"] = config.FLASK_APP_SECRET_KEY
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get('authToken')
        if not token:
            return redirect("/login")

        user = database.get_user_by_token(token)
        if not user:
            return redirect("/login")
        if user.get("status", database.Status.PENDING.value) == database.Status.PENDING.value:
            return redirect(f"/set_new_password?token={user['token']}")

        token_time = helper.try_to_int(user.get("timestamp", 0))
        if not token_time:
            return redirect("/login")

        if (time.time() - token_time) > config.TOKEN_DURATION:
            language, _ = helper.get_language_for_user(user)
            flash(language.get("session_expired", "session_expired"))

            g.user = None
            response = redirect("/login")
            response.set_cookie("authToken", "", expires=0)  # Clear expired cookie
            return response

        g.user = user
        return func(*args, **kwargs)

    return wrapper


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():

    language = database.get_language(helper.DEFAULT_LANG_ID)

    if request.method == "GET":
        database.init_db()

        return render_template(
            "login.html",
            language=language,
            colors=helper.default_colors,
            show_logout=False,
            show_home=False
        )

    email = request.form.get("email")
    password = request.form.get("password")

    user = database.get_user_by_email(email)
    token = helper.generate_token()

    if not user:
        flash(language.get("bad_login", "bad_login"))
        return redirect("/login")

    if user.get("status", database.Status.PENDING.value) == database.Status.PENDING.value:
        if helper.check_token_expired(user):
            database.update_user(email=email, token=token)
        else:
            token = user["token"]

        return redirect(f"/set_new_password?token={token}")

    if not helper.check_hashed_string(password, user.get("password")):
        flash(language.get("bad_login", "bad_login"))
        return redirect("/login")

    database.update_user(email=email, token=token)

    response = redirect("/")
    response.set_cookie("authToken", token, httponly=True, secure=False, samesite="Lax")
    return response


@app.route("/logout")
def logout():
    helper.run_ustreamer(False)

    response = redirect('/login')
    response.set_cookie('authToken', '', expires=0)
    return response


@app.route("/set_new_password", methods=["GET", "POST"])
def set_new_password():
    language = database.get_language(helper.DEFAULT_LANG_ID)

    if request.method == "GET":
        args = request.args
        token = args.get("token")

        if not token:
            flash(language.get("no_token", "no_token"))
            return redirect("/login")

        user = database.get_user_by_token(token)

        if not user:
            flash(language.get("no_token", "no_token"))
            return redirect("/login")

        if (time.time() - user.get("timestamp", 0)) > config.RESET_TOKEN_DURATION:
            flash(language.get("link_expired", "link_expired"))
            return redirect("/login")

        return render_template("set_new_password.html", token=token, language=language, colors=helper.default_colors,
                               show_logout=False, show_home=True)

    password1 = request.form.get("password1")
    password2 = request.form.get("password2")
    token = request.form.get("token")

    user = database.get_user_by_token(token=token)
    if not user:
        flash(language.get("invalid_reset_link", "invalid_reset_link"))
        return redirect("/login")

    if (time.time() - user["timestamp"]) > config.RESET_TOKEN_DURATION:
        flash(language.get("link_expired", "link_expired"))
        return redirect("/login")

    if password1 != password2:
        flash(language.get("password_mismatch", "password_mismatch"))
        return render_template("set_new_password.html", password1=password1, password2=password2, token=token, language=language,
                               show_logout=False, show_home=True)

    if len(password1) < 6 or " " in password1:
        flash(language.get("bad_password_format", "bad_password_format"))
        return render_template("set_new_password.html", language=language, show_logout=False, show_home=True)

    password = helper.hash_string(password1)
    database.update_user(email=user["email"], password=password)
    database.update_user(email=user["email"], status=database.Status.ACTIVE.value)

    flash(language.get("password_update_success", "password_update_success"))
    return redirect("/login")


@app.route("/reset_pass", methods=["GET", "POST"])
def reset_pass():
    language = database.get_language(helper.DEFAULT_LANG_ID)

    if request.method == "POST":
        email = request.form.get("email")

        user = database.get_user_by_email(email)

        if user:
            token = helper.generate_token()
            database.update_user(email=email, token=token)

            message = (f"We received a password reset request for your user account. If you did not request it, disregard this e-mail."
                       f"\n To reset your account password, follow this link: {request.host_url}set_new_password?token={token}\n")
            helper.send_email(user["email"], "Reset link for Appointment App", message)

        flash(language.get("password_reset_email_sent", "password_reset_email_sent"))
        return redirect("/login")

    return render_template("reset_pass.html", language=language, colors=helper.default_colors, show_logout=False, show_home=True )


@app.route("/", methods=["GET"])
@login_required
def index():
    args = request.args
    resolution_request = args.get("resolution")

    language = database.get_language(helper.DEFAULT_LANG_ID)

    helper.run_ustreamer(False)
    time.sleep(1)
    resolutions = helper.check_supported_resolutions()

    if resolution_request:
        database.update_user(email=g.user["email"], resolution=resolution_request)
    else:
        resolution_request = g.user.get("resolution")

    helper.run_ustreamer(start=True, resolution=resolution_request)

    stream_host = request.host.split(':')[0]

    return render_template(
        "index.html",
        time=int(time.time()),
        show_full_navigation=True,
        language=language,
        colors=helper.default_colors,
        show_logout=True,
        show_home=False,
        resolutions=resolutions,
        current_res=resolution_request,
        stream_host=stream_host
    )



if __name__ == "__main__":
    Flask.run(app, host="0.0.0.0", port=config.SERVER_PORT, debug=False)
