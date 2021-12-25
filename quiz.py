#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  quiz.py

from flask import Flask, g, session
from flask_login import LoginManager
from urllib.parse import urlparse, urljoin
from modele import *
from flask import render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, login_user, logout_user, current_user
from forms import *


app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY='bardzotajnyklucz',
))

login_manager = LoginManager()
login_manager.init_app(app)


@app.before_request
def before_request():
    g.db = baza
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    g.db.close()
    return response


@login_manager.user_loader
def user_loader(id):
    try:
        user = User.get(User.id == int(id))
    except DoesNotExist:
        user = None
    return user

#@login_manager.request_loader
# def request_loader(request):
#    nazwa = request.form.get('nazwa')
#    return User.get(User.nazwa == nazwa)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


@app.route("/")
def hello():
    # return "Hello World!"
    return render_template('index.html')


@app.route("/lista")
def lista():
    pytania = Pytanie().select()
    if not pytania.count():
        pass
    return render_template('lista.html', pytania=pytania)


@app.route("/quiz", methods=['GET', 'POST'])
def quiz():

    print(request.form)

    if request.method == 'POST':
        wynik = 0
        for pid, oid in request.form.items():
            if Odpowiedz().get(Odpowiedz.id == int(oid)).odpok:
                wynik += 1

        flash('Poprawnych odpowiedzi: {}'.format(wynik), 'info')
        return redirect(url_for('hello'))

    pytania = Pytanie().select().join(Odpowiedz).distinct()
    return render_template('quiz.html', pytania=pytania)


def flash_errors(form):
    """Odczytanie wszystkich błędów formularza i przygotowanie komunikatów"""
    for field, errors in form.errors.items():
        for error in errors:
            if type(error) is list:
                error = error[0]
            flash("Błąd: {}. Pole: {}".format(
                error,
                getattr(form, field).label.text))


@app.route("/dodaj", methods=['GET', 'POST'])
@login_required
def dodaj():
    form = PytForm()
    form.kategoria.choices = [(k.id, k.kategoria) for k in Kategoria.select()]

    if form.validate_on_submit():
        p = Pytanie(pytanie=form.pytanie.data, kategoria=form.kategoria.data)
        p.save()
        for o in form.odpowiedzi.data:
            odp = Odpowiedz(odpowiedz=o['odpowiedz'], pytanie=p.id,
                            odpok=int(o['odpok']))
            odp.save()
        flash("DOdano pytanie: {}".format(form.pytanie.data))
        return redirect(url_for("lista"))
    elif request.method == "POST":
        flash_errors(form)

    return render_template("dodaj.html", form=form)


def get_or_404(pid):
    try:
        p = Pytanie.get_by_id(pid)
        return p
    except Pytanie.DoesNotExist:
        abort(404)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/usun/<int:pid>", methods=['GET', 'POST'])
def usun(pid):
    p = get_or_404(pid)
    if request.method == "POST":
        flash("Usunięto pytanie: {}".format(p.pytanie))
        for o in Odpowiedz.select().where(Odpowiedz.pytanie == p.id):
            o.delete_instance()
        p.delete_instance()
        return redirect(url_for("lista"))

    return render_template("usun.html", pytanie=p)


@app.route("/edytuj/<int:pid>", methods=['GET', 'POST'])
def edytuj(pid):
    p = get_or_404(pid)
    form = PytForm(obj=p)
    form.kategoria.choices = [(k.id, k.kategoria) for k in Kategoria.select()]
    form.kategoria.data = p.kategoria.id

    if form.validate_on_submit():
        p.pytanie = form.pytanie.data
        p.kategoria = form.kategoria.data
        p.save()
        for o in form.odpowiedzi.data:
            odp = Odpowiedz.get_by_id(o['id'])
            odp.odpowiedz = o['odpowiedz']
            odp.odpok = int(o['odpok'])
            odp.save()
        flash("Zaktualizowano pytanie: {}".format(form.pytanie.data))
        return redirect(url_for("lista"))
    elif request.method == "POST":
        flash_errors(form)

    odpowiedzi = []
    for o in Odpowiedz.select().where(Odpowiedz.pytanie == p.id).dicts():
        odpowiedzi.append(o)
    form.odpowiedzi(data=odpowiedzi)

    return render_template("edytuj.html", form=form)


@app.route("/logowanie", methods=["GET", "POST"])
def logowanie():
    form = LoginForm()
    if form.validate_on_submit():
        nazwa = form.nazwa.data
        haslo = form.haslo.data
        try:
            user = User.get(User.nazwa == nazwa and User.haslo == haslo)
        except DoesNotExist:
            user = User()
            user.id = None

        print(user.is_active)
        if user.id:
            login_user(user)
            flash('Zalogowano.')
            next = request.args.get('next')
            if not is_safe_url(next):
                return abort(400)

            return redirect(next or url_for('zalogowano'))
        else:
            flash('Błędna nazwa lub hasło.')

    return render_template('logowanie.html', form=form)


@app.route("/wylogowanie")
@login_required
def logout():
    logout_user()
    flash("Wylogowano.")
    return render_template("index.html")


@app.route("/zalogowano")
@login_required
def zalogowano():
    return render_template("zalogowano.html")


if __name__ == '__main__':
    app.run(debug=True)
