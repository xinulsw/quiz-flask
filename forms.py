#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# forms.py

from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, BooleanField, SelectField
from wtforms import FieldList, FormField
from wtforms.validators import DataRequired

blad1 = "To pole jest wymagane!"


class OdpForm(FlaskForm):
    id = HiddenField()
    odpowiedz = StringField("Odpowiedź: ",
                            validators=[DataRequired(message=blad1)])
    pytanie = HiddenField()
    odpok = BooleanField("Poprawna: ")


class PytForm(FlaskForm):
    id = HiddenField()
    pytanie = StringField("Pytanie: ", validators=[
                          DataRequired(message=blad1)])
    kategoria = SelectField("Kategoria: ", coerce=int)
    odpowiedzi = FieldList(FormField(OdpForm), min_entries=3)


class LoginForm(FlaskForm):
    id = HiddenField()
    nazwa = StringField("Nazwa użytkownika: ", validators=[
                        DataRequired(message=blad1)])
    haslo = StringField("Hasło: ", validators=[DataRequired(message=blad1)])
