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
    cur.execute("""SELECT uporabnisko_ime,ime,priimek,datum_rojstva,drzavljanstvo,clanstvo,st_izleta 
                FROM oseba ORDER BY priimek, ime""")
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

# transport

@get('/transport')
def transport():
    cur.execute("SELECT * FROM transport;")
    return template('transport.html', transport=cur)

@get('/dodaj_transport')
def dodaj_transport():
    return template('dodaj_transport.html', id_transporta='', vrsta_transporta='', cena='', napaka=None)

@post('/dodaj_transport')
def dodaj_transport_post():
    id_transporta = request.forms.id_transporta
    vrsta_transporta = request.forms.vrsta_transporta
    cena = request.forms.cena
    try:
        cur.execute("INSERT INTO transport (id_transporta, vrsta_transporta, cena) VALUES (%s, %s, %s)",
                    (id_transporta, vrsta_transporta, cena))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('dodaj_transport.html', id_transporta=id_transporta, vrsta_transporta=vrsta_transporta, cena=cena,
                        napaka='Zgodila se je napaka: %s' % ex)
    redirect(url('/transport'))
  
# namestitev

@get('/namestitev')
def namestitev():
    cur.execute("SELECT id_namestitve, vrsta_namestitve, cena FROM namestitev;")
    return template('namestitev.html', namestitev=cur)

@get('/dodaj_namestitev')
def dodaj_namestitev():
    return template('dodaj_namestitev.html', id_namestitve='', vrsta_namestitve='', cena='', napaka=None)

@post('/dodaj_namestitev')
def dodaj_namestitev_post():
    id_namestitve = request.forms.id_namestitve
    vrsta_namestitve = request.forms.vrsta_namestitve
    cena = request.forms.cena
    try:
        cur.execute("INSERT INTO namestitev (id_namestitve, vrsta_namestitve, cena) VALUES (%s, %s, %s)",
                    (id_namestitve, vrsta_namestitve, cena))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('dodaj_namestitev.html', id_namestitve=id_namestitve, vrsta_namestitve=vrsta_namestitve, cena=cena,
                        napaka='Zgodila se je napaka: %s' % ex)
    redirect(url('/namestitev'))

# skupine

@get('/skupine')
def skupine():
    cur.execute("SELECT id_skupine,ime_skupine FROM skupina;")
    return template('skupine.html', skupine=cur)

@get('/dodaj_skupino')
def dodaj_skupino():
    return template('dodaj_skupino.html', id_skupine='', ime_skupine='', napaka=None)

@post('/dodaj_skupino')
def ddodaj_skupino_post():
    id_skupine = request.forms.id_skupine
    ime_skupine = request.forms.ime_skupine
    try:
        cur.execute("INSERT INTO skupina (id_skupine, ime_skupine) VALUES (%s, %s)",
                    (id_skupine, ime_skupine))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('dodaj_skupino.html', id_skupine=id_skupine, ime_skupine=ime_skupine,
                        napaka='Zgodila se je napaka: %s' % ex)
    redirect(url('/skupine'))

@get('/clani_skupine/<x:int>/')
def clani_skupine(x):
    cur.execute("""SELECT uporabnisko_ime,ime,priimek,datum_rojstva,drzavljanstvo,clanstvo,st_izleta 
                FROM oseba WHERE clanstvo = %s""", [x])
    return template('clani_skupine.html', x=x, oseba=cur)

######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)