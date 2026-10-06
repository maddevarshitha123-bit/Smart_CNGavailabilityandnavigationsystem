"""MySQL access. Every query uses %s placeholders (parameterized) to stop SQL injection."""
import mysql.connector
from mysql.connector import Error
import config


class DatabaseError(Exception):
    """Friendly wrapper so pages can show a message instead of crashing."""


def get_connection():
    try:
        return mysql.connector.connect(
            host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
            database=config.DB_NAME, connection_timeout=5)
    except Error as e:
        raise DatabaseError(f"Cannot connect to MySQL. Check .env and that MySQL is running. ({e})")


def query(sql, params=(), fetch="all", commit=False):
    """Run one SQL statement. fetch: 'all' | 'one' | None. Returns rows or lastrowid."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        if commit:
            conn.commit()
            return cur.lastrowid
        if fetch == "one":
            return cur.fetchone()
        return cur.fetchall() if fetch == "all" else None
    except Error as e:
        raise DatabaseError(f"Database error: {e}")
    finally:
        conn.close()


def test_connection():
    try:
        get_connection().close()
        return True
    except DatabaseError:
        return False


# ---------- users ----------
def get_user_by_email(email):
    return query("SELECT * FROM users WHERE email=%s", (email,), fetch="one")

def create_user(name, email, password_hash, role="user"):
    return query("INSERT INTO users (name,email,password_hash,role) VALUES (%s,%s,%s,%s)",
                 (name, email, password_hash, role), commit=True)

def update_user_name(user_id, name):
    query("UPDATE users SET name=%s WHERE user_id=%s", (name, user_id), commit=True)

def update_password(user_id, password_hash):
    query("UPDATE users SET password_hash=%s WHERE user_id=%s", (password_hash, user_id), commit=True)


# ---------- stations ----------
LATEST_STATUS_SQL = """
SELECT s.*, ss.availability, ss.queue_length, ss.waiting_time, ss.traffic_level, ss.updated_at
FROM stations s
LEFT JOIN station_status ss ON ss.status_id = (
    SELECT MAX(status_id) FROM station_status WHERE station_id = s.station_id)
"""

def get_stations_with_status():
    return query(LATEST_STATUS_SQL + " ORDER BY s.name")

def add_station(name, address, lat, lon, phone, hours, status):
    return query("INSERT INTO stations (name,address,latitude,longitude,phone,operating_hours,status) "
                 "VALUES (%s,%s,%s,%s,%s,%s,%s)", (name, address, lat, lon, phone, hours, status), commit=True)

def update_station(sid, name, address, lat, lon, phone, hours, status):
    query("UPDATE stations SET name=%s,address=%s,latitude=%s,longitude=%s,phone=%s,"
          "operating_hours=%s,status=%s WHERE station_id=%s",
          (name, address, lat, lon, phone, hours, status, sid), commit=True)

def delete_station(sid):
    query("DELETE FROM stations WHERE station_id=%s", (sid,), commit=True)

def add_status(sid, availability, queue, wait, traffic):
    return query("INSERT INTO station_status (station_id,availability,queue_length,waiting_time,traffic_level) "
                 "VALUES (%s,%s,%s,%s,%s)", (sid, availability, queue, wait, traffic), commit=True)

def get_status_history(limit=200):
    return query("SELECT ss.*, s.name FROM station_status ss JOIN stations s USING(station_id) "
                 "ORDER BY ss.updated_at DESC, ss.status_id DESC LIMIT %s", (limit,))


# ---------- predictions ----------
def log_prediction(sid, availability, wait):
    return query("INSERT INTO prediction_history (station_id,predicted_availability,predicted_waiting_time) "
                 "VALUES (%s,%s,%s)", (sid, availability, wait), commit=True)

def get_prediction_history(limit=200):
    return query("SELECT p.*, s.name FROM prediction_history p JOIN stations s USING(station_id) "
                 "ORDER BY p.prediction_time DESC, p.prediction_id DESC LIMIT %s", (limit,))
