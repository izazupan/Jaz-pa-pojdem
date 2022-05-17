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
import hashlib
import bottle

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# odkomentiraj, če želiš sporočila o napakah
debug = True

skrivnost = "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr"

def nastaviSporocilo(sporocilo = None):
    # global napakaSporocilo
    staro = request.get_cookie("sporocilo", secret=skrivnost)
#    if sporocilo is None:
#        bottle.Response.delete_cookie(key='sporocilo', path='/', secret=skrivnost)
#    else:
#        bottle.Response.set_cookie(key='sporocilo', value=sporocilo, path="/", secret=skrivnost)
    return staro 

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

#začetno stran je treba še popraviti
@get('/')
def hello():
#    return 'Začetna stran'
    return template('zacetna_stran.html')

##########################
# prijava, registracija, odjava

def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()

@get('/registracija')
def registracija_get():
    napaka = nastaviSporocilo()
    return template('registracija.html', napaka=napaka)

@post('/registracija')
def registracija_post():
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = request.forms.geslo
    geslo2 = request.forms.geslo2
    ime = request.forms.ime
    priimek = request.forms.priimek
    datum_rojstva = request.forms.datum_rojstva
    if uporabnisko_ime is None or geslo is None or geslo2 is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect('/registracija')
        return
    oseba = cur 
    uporabnik = None
    try: 
        uporabnik = cur.execute("SELECT * FROM oseba WHERE uporabnisko_ime = ?", [uporabnisko_ime])
    except:
        uporabnik = None
    if uporabnik is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect('/registracija')
        return
    if len(geslo) < 4:
        nastaviSporocilo('Geslo mora imeti vsaj 4 znake.') 
        redirect('/registracija')
        return
    if geslo != geslo2:
        nastaviSporocilo('Gesli se ne ujemata.') 
        redirect('/registracija')
        return
    zgostitev = hashGesla(geslo)
    cur.execute("""INSERT INTO oseba
                (uporabnisko_ime,ime,priimek,datum_rojstva,geslo)
                VALUES (%s, %s, %s, %s, %s)""", (uporabnisko_ime,ime,priimek,datum_rojstva, zgostitev))
    bottle.Response.set_cookie(key='uporabnisko_ime', value=uporabnisko_ime, path='/', secret=skrivnost)
    redirect('/osebe')


@get('/prijava')
def prijava_get():
    return template('prijava.html')

@post('/prijava')
def prijava_post():
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = request.forms.geslo
    if uporabnisko_ime is None or geslo is None:
        nastaviSporocilo('Uporabniško ima in geslo morata biti neprazna') 
        redirect('/prijava')
        return
    oseba = cur   
    hashBaza = None
    try: 
        hashBaza = cur.execute("SELECT geslo FROM oseba WHERE uporabnisko_ime = %s", [uporabnisko_ime])
        hashBaza = hashBaza[0]
    except:
        hashBaza = None
    if hashBaza is None:
        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
        redirect('/prijava')
        return
    if hashGesla(geslo) != hashBaza:
        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
        redirect('/prijava')
        return
    bottle.Response.set_cookie(key='uporabnisko_ime', value=uporabnisko_ime, secret=skrivnost)
    redirect('/komitenti')
    
@get('/odjava')
def odjava_get():
    bottle.Response.delete_cookie(key='uporabnisko_ime')
    redirect('/prijava')


##################################


# osebe

@get('/osebe')
def index():
    cur.execute("""SELECT uporabnisko_ime,ime,priimek,datum_rojstva,drzavljanstvo,clanstvo,st_izleta 
                FROM oseba ORDER BY priimek, ime""")
    return template('osebe.html', oseba=cur)

# obiski

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
    cur.execute("SELECT * FROM transport ORDER BY id_transporta;")
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

@get('/uredi_transport')
def uredi_transport():
    return template('uredi_transport.html', id_transporta='', vrsta_transporta='', cena='', napaka=None)

@post('/uredi_transport')
def uredi_transport_post():
    id_transporta = request.forms.id_transporta
    vrsta_transporta = request.forms.vrsta_transporta
    cena = request.forms.cena
    try:
        cur.execute("UPDATE transport SET vrsta_transporta=%s, cena=%s WHERE id_transporta=%s",
                    (vrsta_transporta, cena, id_transporta))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('uredi_transport.html', id_transporta=id_transporta, vrsta_transporta=vrsta_transporta, cena=cena,
                        napaka='Zgodila se je napaka: %s' % ex)
    redirect(url('/transport'))

# @get('/brisi_transport/<id_transporta>/')
# def brisi_transport(id_transporta):
#     cur.execute("""SELECT * FROM transport WHERE id_transporta = %s""", [id_transporta])
#     return template('transport.html', id_transporta=id_transporta, transport=cur)
# 
# @post('/brisi_transport/<id_transporta>') 
# def brisi_transport_post(id_transporta):
#     id_transporta = request.forms.id_transporta
#     try:
#         cur.execute("DELETE FROM transport WHERE id_transporta = %s", [id_transporta])
#         conn.commit()
#     except Exception as ex:
#         conn.rollback()
#         return template('transport.html', id_transporta=id_transporta,
#                         napaka='Zgodila se je napaka: %s' % ex)
#     redirect(url('/transport'))

# namestitev

@get('/namestitev')
def namestitev():
    cur.execute("SELECT * FROM namestitev ORDER BY id_namestitve;")
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

@get('/uredi_namestitev')
def uredi_namestitev():
    return template('uredi_namestitev.html', id_namestitve='', vrsta_namestitve='', cena='', napaka=None)

@post('/uredi_namestitev')
def uredi_namestitev_post():
    id_namestitve = request.forms.id_namestitve
    vrsta_namestitve = request.forms.vrsta_namestitve
    cena = request.forms.cena
    try:
        cur.execute("UPDATE namestitev SET vrsta_namestitve=%s, cena=%s WHERE id_namestitve=%s",
                    (vrsta_namestitve, cena, id_namestitve))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('uredi_namestitev.html', id_namestitve=id_namestitve, vrsta_namestitve=vrsta_namestitve, cena=cena,
                        napaka='Zgodila se je napaka: %s' % ex)
    redirect(url('/namestitev'))

# skupine

@get('/skupine')
def skupine():
    cur.execute("SELECT * FROM skupina ORDER BY id_skupine;")
    return template('skupine.html', skupine=cur)

@get('/dodaj_skupino')
def dodaj_skupino():
    return template('dodaj_skupino.html', id_skupine='', ime_skupine='', napaka=None)

@post('/dodaj_skupino')
def dodaj_skupino_post():
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

@get('/uredi_skupino')
def uredi_skupino():
    return template('uredi_skupino.html', id_skupine='', ime_skupine='', napaka=None)

@post('/uredi_skupino')
def uredi_skupino_post():
    id_skupine = request.forms.id_skupine
    ime_skupine = request.forms.ime_skupine
    try:
        cur.execute("UPDATE skupina SET ime_skupine=%s WHERE id_skupine=%s",
                    (ime_skupine, id_skupine))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('uredi_skupino.html', id_skupine=id_skupine, ime_skupine=ime_skupine,
                        napaka='Zgodila se je napaka: %s' % ex)
    redirect(url('/skupine'))

######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)