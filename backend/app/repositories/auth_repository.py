import json
import time
from app.db import get_conn

# ---------- OAuth State ----------
def create_state(state: str, ttl_sec: int) -> None:
    expires_at = int(time.time()) + ttl_sec
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO oauth_state (state, expires_at) VALUES (?, ?)", (state, expires_at))
    conn.commit()
    conn.close()

def consume_state(state: str) -> bool:
    now = int(time.time())
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT state, expires_at FROM oauth_state WHERE state = ?", (state,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return False

    # one-time use
    cur.execute("DELETE FROM oauth_state WHERE state = ?", (state,))
    conn.commit()
    conn.close()

    return row["expires_at"] >= now

def cleanup_expired_states() -> None:
    now = int(time.time())
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM oauth_state WHERE expires_at < ?", (now,))
    conn.commit()
    conn.close()

# ---------- Sessions ----------
def create_session(session_id: str, token_data: dict, ttl_sec: int) -> None:
    now = int(time.time())
    expires_at = now + ttl_sec
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_session (session_id, token_data, expires_at, created_at) VALUES (?, ?, ?, ?)",
        (session_id, json.dumps(token_data), expires_at, now),
    )
    conn.commit()
    conn.close()

def get_session(session_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_session WHERE session_id = ?", (session_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "session_id": row["session_id"],
        "token_data": json.loads(row["token_data"]),
        "expires_at": row["expires_at"],
        "created_at": row["created_at"],
    }

def update_session_token(session_id: str, token_data: dict, ttl_sec: int) -> None:
    expires_at = int(time.time()) + ttl_sec
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE user_session SET token_data = ?, expires_at = ? WHERE session_id = ?",
        (json.dumps(token_data), expires_at, session_id),
    )
    conn.commit()
    conn.close()

def delete_session(session_id: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_session WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

def cleanup_expired_sessions() -> None:
    now = int(time.time())
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_session WHERE expires_at < ?", (now,))
    conn.commit()
    conn.close()
