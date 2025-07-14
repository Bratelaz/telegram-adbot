
import sqlite3

def init_db():
    conn = sqlite3.connect("ads.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        description TEXT,
        price TEXT,
        city TEXT,
        contact TEXT,
        photo_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def save_ad(user_id, title, description, price, city, contact, photo_id):
    conn = sqlite3.connect("ads.db")
    c = conn.cursor()
    c.execute("INSERT INTO ads (user_id, title, description, price, city, contact, photo_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (user_id, title, description, price, city, contact, photo_id))
    conn.commit()
    conn.close()

def get_ads_by_user(user_id):
    conn = sqlite3.connect("ads.db")
    c = conn.cursor()
    c.execute("SELECT id, title, price FROM ads WHERE user_id = ?", (user_id,))
    ads = c.fetchall()
    conn.close()
    return ads

def delete_ad(ad_id, user_id):
    conn = sqlite3.connect("ads.db")
    c = conn.cursor()
    c.execute("DELETE FROM ads WHERE id = ? AND user_id = ?", (ad_id, user_id))
    conn.commit()
    conn.close()
