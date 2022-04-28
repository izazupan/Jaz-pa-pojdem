# uvozimo ustrezne podatke za povezavo
import auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
        CREATE TABLE namestitev (
            id SERIAL UNIQUE PRIMARY KEY,
            vrsta_namestitve TEXT NOT NULL,
            cena DECIMAL NOT NULL
            );
    """)
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE namestitev;
    """)
    conn.commit()

def uvozi_podatke():
    with open("podatki/namestitev.csv", encoding="utf-16", errors='ignore') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO transport
                (vrsta_namestitve, cena)
                VALUES (%s, %s)
                """, r)
            rid, = cur.fetchone()
            print("Uvožena vrsta namestitve %s z ID-jem %d" % (r[0], rid))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

ustvari_tabelo()