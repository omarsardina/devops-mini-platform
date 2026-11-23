import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        database=os.environ.get("DB_NAME", "platform_db"),
        user=os.environ.get("DB_USER", "admin"),
        password=os.environ.get("DB_PASS", "secret123"),
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS visits (id SERIAL PRIMARY KEY, count INT);")
    cur.execute("SELECT count FROM visits WHERE id = 1;")
    if cur.fetchone() is None:
        cur.execute("INSERT INTO visits (id, count) VALUES (1, 0);")
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def home():
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE visits SET count = count + 1 WHERE id = 1 RETURNING count;")
    visits = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "running", "total_visits": visits})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
