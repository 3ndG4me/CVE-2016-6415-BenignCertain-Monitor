import sqlite3
import os
import subprocess
import pathlib
import pandas as pd
import sys
import time

conn = sqlite3.connect('details.db')
c = conn.cursor()
c.execute("CREATE TABLE if not exists result(string text , count integer)")
conn.commit()

host = sys.argv[1]

path = 'benigncertain'
file = pathlib.Path(f'{path}/{host}.bin')

try:
    cp = subprocess.run([f"python2.7 benign.py {host} -o {host}.bin -n 10000"], cwd=path, universal_newlines=True, shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)

    output = subprocess.run([f"strings {host}.bin"], cwd=path, universal_newlines=True, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    words = output.stdout.split()

    if words and file.exists():
        for word in words:
            c.execute("SELECT count FROM result WHERE string=?", (word,))
            query = c.fetchone()
            if query is None:
                c.execute("INSERT INTO result(string, count) VALUES(?,?)", (word, 1))
            else:
                c.execute("UPDATE result SET count =? WHERE string=?", (query[0] + 1, word,))

        conn.commit()
        os.remove(f'{path}/{host}.bin')

        print(pd.read_sql_query("SELECT * FROM result order by count DESC", conn))

except subprocess.TimeoutExpired:
    print('\'bc-id\' binary timed out, this will happen frequently with some hosts.' )

