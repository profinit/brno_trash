from flask import Flask
import sqlite3

app = Flask(__name__)
callback = lambda x: x


def create_db():
    conn = sqlite3.connect('../model/active_containers.db', )
    c = conn.cursor()
    c.execute(f"CREATE TABLE IF NOT EXISTS active_bins (bin_id integer UNIQUE);")
    conn.commit()
    c.close()


@app.route('/activate/<int:container_id>', methods=['GET'])
def index(container_id: int):
    conn = sqlite3.connect('../model/active_containers.db')
    c = conn.cursor()
    c.execute(f"INSERT OR IGNORE INTO active_bins VALUES (?)", (container_id,))

    r = c.execute(f"SELECT * FROM active_bins")
    for i in r:
        print(i)

    conn.commit()
    c.close()

    return f"<!DOCTYPE html><html><body>Container {container_id} marked as full.</body></html>"

if __name__ == "__main__":
    app.run()