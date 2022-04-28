import os
cwd = os.getcwd()
print("Current working directory: {0}".format(cwd))

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
        CREATE TABLE drzava (
            kratica TEXT PRIMARY KEY NOT NULL,
            ime_drzave TEXT NOT NULL,
        );
    """) 
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE drzava;
    """)
    conn.commit()

def uvozi_podatke():
    with open("podatki/drzava.csv", encoding="UTF-8") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            r = [None if x in ('', '-') else x for x in r]
            cur.execute("""
                INSERT INTO drzava
                (kratica,ime_drzave)
                VALUES (%s, %s)
                RETURNING ime_drzave
            """, r)
            print("Uvožena država %s s kratico %s" % (r[1], r[0]))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 