# uvozimo ustrezne podatke za povezavo
import auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
        CREATE TABLE skupina (
            id_skupine INTEGER PRIMARY KEY NOT NULL,
            ime_skupine TEXT NOT NULL
        );
    """) 
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE skupina;
    """)
    conn.commit()

def uvozi_podatke():
    with open("podatki/skupina.csv", encoding="utf-16", errors='ignore') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO skupina
                (id_skupine,ime_skupine)
                VALUES (%s, %s)
            """, r)
            print("Uvožena skupina %s z ID-jem %s" % (r[1], r[0]))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
