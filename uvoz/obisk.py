# uvozimo ustrezne podatke za povezavo
import auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
        CREATE TABLE obisk (
            st_izleta INTEGER PRIMARY KEY,
            st_dni NUMERIC NOT NULL,
            id_mesta NUMERIC REFERENCES mesto(id),
            id_namestitve INTEGER REFERENCES namestitev(id_namestitve),
            id_transporta INTEGER REFERENCES transport(id_transporta)
            );
    """)
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE obisk;
    """)
    conn.commit()

def uvozi_podatke():
    with open("podatki/obisk.csv", encoding="utf-8", errors='ignore') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            cur.execute("""
                INSERT INTO obisk
                (st_izleta,st_dni,id_mesta,id_namestitve,id_transporta)
                VALUES (%s, %s, %s,%s, %s)
                """, r)
            # rid, = cur.fetchone()
            print("Uvožen izlet z ID-jem %s" % (r[0]))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

#pobrisi_tabelo()
#ustvari_tabelo()
uvozi_podatke()