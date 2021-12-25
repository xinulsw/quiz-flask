#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  modele.py

from peewee import *
from flask_login import UserMixin


baza_plik = 'quiz.db'
baza = SqliteDatabase(baza_plik)  # instancja bazy


# MODELE
class BazaModel(Model):
    class Meta:
        database = baza


class Kategoria(BazaModel):
    kategoria = CharField(null=False)


class Pytanie(BazaModel):
    pytanie = CharField(null=False)
    kategoria = ForeignKeyField(Kategoria, related_name='pytania')


class Odpowiedz(BazaModel):
    odpowiedz = CharField(null=False)
    pytanie = ForeignKeyField(Pytanie, related_name='odpowiedzi')
    odpok = IntegerField(default=0)


class User(BazaModel, UserMixin):
    nazwa = CharField(null=False)
    haslo = CharField(null=False)
