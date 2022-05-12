#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import get, post, run, request, template, redirect, static_file, url

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# odkomentiraj, če želiš sporočila o napakah
debug = True

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get('/')
def index():
    cur.execute("SELECT uporabnisko_ime,ime,priimek,datum_rojstva,drzavljanstvo,clanstvo,st_izleta FROM oseba ORDER BY priimek, ime")
    return template('osebe.html', oseba=cur)

@get('/obisk')
def obiski():
    cur.execute("""SELECT st_izleta,st_dni,ime_mesta,ime_drzave,vrsta_transporta,vrsta_namestitve
                FROM obisk
                JOIN mesto ON obisk.id_mesta=mesto.id
                JOIN drzava ON mesto.kratica_drzave=drzava.kratica
                JOIN transport ON obisk.id_transporta=transport.id_transporta
                JOIN namestitev ON obisk.id_namestitve=namestitev.id_namestitve;""")
    return template('obisk.html', obisk=cur)

#@get('/dodaj_transakcijo')
#def dodaj_transakcijo():
#    return template('dodaj_transakcijo.html', znesek='', racun='', opis='', napaka=None)
#
#@post('/dodaj_transakcijo')
#def dodaj_transakcijo_post():
#    znesek = request.forms.znesek
#    racun = request.forms.racun
#    opis = request.forms.opis
#    try:
#        cur.execute("INSERT INTO transakcija (znesek, racun, opis) VALUES (%s, %s, %s)",
#                    (znesek, racun, opis))
#        conn.commit()
#    except Exception as ex:
#        conn.rollback()
#        return template('dodaj_transakcijo.html', znesek=znesek, racun=racun, opis=opis,
#                        napaka='Zgodila se je napaka: %s' % ex)
#    redirect(url('index'))

######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)