import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, redirect, session, url_for, render_template, request
from config import Config
from utils.suap_oauth import make_suap_session

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    suap = make_suap_session()
    auth_url, state = suap.authorization_url(Config.SUAP_BASE_URL + "/o/authorize/")
    session['oauth_state'] = state
    return redirect(auth_url)

@app.route('/login/authorized')
def authorized():
    suap = make_suap_session(state=session.get('oauth_state'))
    token = suap.fetch_token(
        Config.SUAP_BASE_URL + "/o/token/",
        client_secret=Config.SUAP_CLIENT_SECRET,
        authorization_response=request.url
    )
    session['oauth_token'] = token

    suap = make_suap_session(token=token)
    user_response = suap.get(Config.SUAP_BASE_URL + "/api/v2/minhas-informacoes/meus-dados/")
    if user_response.status_code == 200:
        user = user_response.json()
    else:
        user = {}

    avatar_response = suap.get(Config.SUAP_BASE_URL + "/api/v2/minhas-informacoes/meu-avatar/")
    if avatar_response.status_code == 200:
        avatar = avatar_response.json()
        session['avatar_url'] = avatar.get('foto')
    else:
        session['avatar_url'] = None

    session['user'] = user

    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template("profile.html", user=session['user'], avatar=session['avatar_url'])

@app.route('/boletim')
def boletim():
    if 'oauth_token' not in session:
        return redirect(url_for('index'))

    ano = request.args.get('ano', '2023')
    suap = make_suap_session(token=session['oauth_token'])
    boletim_response = suap.get(Config.SUAP_BASE_URL + f"/api/v2/minhas-informacoes/boletim/{ano}/")
    if boletim_response.status_code == 200:
        boletim_json = boletim_response.json()
        # Se o boletim é um dicionário, converta para lista
        boletim = list(boletim_json.values()) if isinstance(boletim_json, dict) else boletim_json
    else:
        boletim = []

    return render_template("boletim.html", boletim=boletim, ano=ano, user=session['user'], avatar=session['avatar_url'])
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)