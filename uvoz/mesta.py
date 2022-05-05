# uvozimo ustrezne podatke za povezavo
import auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
        CREATE TABLE mesto (
            id NUMERIC PRIMARY KEY,
            ime_mesta TEXT NOT NULL,
            kratica_drzave TEXT NOT NULL REFERENCES drzava(kratica)
            );
    """)
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE mesto;
    """)
    conn.commit()

def uvozi_podatke():
    with open("podatki/mesto.csv", encoding="utf-8", errors='ignore') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO mesto
                (id, ime_mesta, kratica_drzave)
                VALUES (%s, %s, %s)
                """, r)
            # rid, = cur.fetchone()
            print("Uvoženo mesto %s iz %s z ID-jem %s" % (r[1], r[2], r[0]))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

#pobrisi_tabelo()
#ustvari_tabelo()
#uvozi_podatke()