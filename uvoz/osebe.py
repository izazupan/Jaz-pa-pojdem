# uvozimo ustrezne podatke za povezavo
import auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
    CREATE TABLE oseba (
        uporabnisko_ime TEXT PRIMARY KEY,
        ime TEXT NOT NULL,
        priimek TEXT NOT NULL,
        datum_rojstva DATE NOT NULL
    );
    """) 
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE oseba;
    """)
    conn.commit()

def uvozi_podatke():
    with open("podatki/oseba.csv", encoding="utf-8", errors='ignore') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO oseba
                (uporabnisko_ime,ime,priimek,datum_rojstva)
                VALUES (%s, %s, %s, %s)
            """, r)
            print("Uvožena oseba %s z uporabniškim imenom %s" % (r[1], r[0]))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 