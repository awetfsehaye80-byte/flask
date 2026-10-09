from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import time

app = Flask(__name__)
CORS(app)

conn = sqlite3.connect("rewards.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, balance REAL DEFAULT 0, ads INTEGER DEFAULT 0, invites INTEGER DEFAULT 0, last_ad REAL DEFAULT 0, ads_round INTEGER DEFAULT 0, subscribed INTEGER DEFAULT 0, ref_by INTEGER DEFAULT 0)")
conn.commit()

AD_REWARD = 0.05

@app.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    u = cur.fetchone()
    if not u:
        cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        u = cur.fetchone()
    return jsonify({"balance": u[3], "ads": u[4], "invites": u[5], "last_ad": u[6], "ads_round": u[7], "subscribed": u[8]})

@app.route("/claim", methods=["POST"])
def claim():
    data = request.json
    user_id = data.get("user_id")
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    u = cur.fetchone()
    if not u:
        return jsonify({"error": "User not found"}), 404
    now = time.time()
    bal, ads, rnd, last = u[3], u[4], u[7], u[6]
    if rnd >= 10:
        wait = 1800 - (now - last)
        if wait > 0:
            return jsonify({"error": "Wait " + str(int(wait//60)) + " min"}), 400
        else:
            rnd = 0
    cur.execute("UPDATE users SET balance=?, ads=?, ads_round=?, last_ad=? WHERE user_id=?", (bal + AD_REWARD, ads + 1, rnd + 1, now, user_id))
    conn.commit()
    return jsonify({"success": True, "new_balance": bal + AD_REWARD})

@app.route("/")
def root():
    return jsonify({"status": "AwetFX Mini App API"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
