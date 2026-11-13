import sqlite3, os, hashlib, hmac, secrets, re
from datetime import datetime
DB_PATH=os.environ.get("JUDGEAI_DB_PATH","judgeai.db")

def connect():
    conn=sqlite3.connect(DB_PATH,timeout=20)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL COLLATE NOCASE UNIQUE,
            email TEXT NOT NULL COLLATE NOCASE UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS evaluations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            question TEXT NOT NULL, answer TEXT NOT NULL,
            accuracy REAL, relevance REAL, clarity REAL, completeness REAL,
            overall_score REAL, strengths TEXT, weaknesses TEXT, improvements TEXT,
            verdict TEXT, created_at TEXT NOT NULL, model_name TEXT)""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_user ON evaluations(user_id, id DESC)")
        # Backward-compatible account personalization and scoring preferences.
        existing={row["name"] for row in c.execute("PRAGMA table_info(users)").fetchall()}
        additions={
            "display_name": "TEXT NOT NULL DEFAULT ''",
            "role": "TEXT NOT NULL DEFAULT 'AI Quality Analyst'",
            "bio": "TEXT NOT NULL DEFAULT ''",
            "accent_color": "TEXT NOT NULL DEFAULT '#8B5CF6'",
            "weekly_goal": "INTEGER NOT NULL DEFAULT 20",
            "accuracy_weight": "REAL NOT NULL DEFAULT 25",
            "relevance_weight": "REAL NOT NULL DEFAULT 25",
            "clarity_weight": "REAL NOT NULL DEFAULT 25",
            "completeness_weight": "REAL NOT NULL DEFAULT 25"
        }
        for name, definition in additions.items():
            if name not in existing:
                c.execute(f"ALTER TABLE users ADD COLUMN {name} {definition}")

def _hash(password, salt=None):
    salt=salt or secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,310000)
    return salt.hex()+":"+digest.hex()

def _verify(password, stored):
    try:
        salt_hex,digest_hex=stored.split(":",1)
        actual=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt_hex),310000)
        return hmac.compare_digest(actual.hex(),digest_hex)
    except Exception: return False

def create_user(username,email,password):
    username=(username or "").strip()
    email=(email or "").strip().lower()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", username):
        return False,"Username must be 3–32 characters and use only letters, numbers, dots, underscores or hyphens."
    if len(email)>254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False,"Enter a valid email address."
    if not isinstance(password,str) or not 8<=len(password)<=128:
        return False,"Password must contain 8–128 characters."
    try:
        with connect() as c:
            c.execute("INSERT INTO users(username,email,password_hash,created_at) VALUES(?,?,?,?)",
                      (username,email,_hash(password),datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return True,"Account created."
    except sqlite3.IntegrityError as e:
        msg=str(e).lower()
        if "username" in msg: return False,"That username is already registered."
        if "email" in msg: return False,"That email address is already registered."
        return False,"Unable to create account."

def authenticate_user(identity,password):
    identity=(identity or "").strip()
    if not identity or not isinstance(password,str):
        return None
    with connect() as c:
        row=c.execute("SELECT * FROM users WHERE username=? OR email=?",(identity,identity)).fetchone()
    if row and _verify(password,row["password_hash"]): return dict(row)
    return None

def get_user(user_id):
    with connect() as c:
        row=c.execute("""SELECT id,username,email,created_at,display_name,role,bio,accent_color,weekly_goal,
        accuracy_weight,relevance_weight,clarity_weight,completeness_weight FROM users WHERE id=?""",(user_id,)).fetchone()
    return dict(row) if row else None

def update_profile(user_id,email):
    email=(email or "").strip().lower()
    if len(email)>254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False,"Enter a valid email address."
    try:
        with connect() as c: c.execute("UPDATE users SET email=? WHERE id=?",(email,user_id))
        return True,"Email updated."
    except sqlite3.IntegrityError: return False,"That email is already in use."

def save_evaluation(user_id,question,answer,result,model_name="Manual evaluation"):
    with connect() as c:
        c.execute("""INSERT INTO evaluations(user_id,question,answer,accuracy,relevance,clarity,completeness,
        overall_score,strengths,weaknesses,improvements,verdict,created_at,model_name)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (user_id,question,answer,result["accuracy"],result["relevance"],result["clarity"],result["completeness"],
         result["overall_score"],result.get("strengths",""),result.get("weaknesses",""),result.get("improvements",""),
         result.get("verdict",""),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),model_name))

def get_history(user_id):
    with connect() as c:
        rows=c.execute("""SELECT id,question,answer,accuracy,relevance,clarity,completeness,overall_score,
        strengths,weaknesses,improvements,verdict,created_at,model_name FROM evaluations
        WHERE user_id=? ORDER BY id DESC""",(user_id,)).fetchall()
    return [tuple(r) for r in rows]

def delete_evaluation(user_id,evaluation_id):
    with connect() as c:
        c.execute("DELETE FROM evaluations WHERE id=? AND user_id=?",(evaluation_id,user_id))


def update_preferences(user_id, display_name, role, bio, accent_color, weekly_goal,
                       accuracy_weight, relevance_weight, clarity_weight, completeness_weight):
    weights=[float(accuracy_weight),float(relevance_weight),float(clarity_weight),float(completeness_weight)]
    if any(w < 0 or w > 100 for w in weights) or sum(weights) <= 0:
        return False,"Rubric weights must be between 0 and 100, with a non-zero total."
    if not 1 <= int(weekly_goal) <= 500:
        return False,"Weekly goal must be between 1 and 500."
    if len(display_name.strip()) > 60 or len(role.strip()) > 60 or len(bio.strip()) > 240:
        return False,"Please keep profile fields within their character limits."
    allowed={"#8B5CF6","#36C8F4","#35D6A0","#F2B85B","#F472B6"}
    if accent_color not in allowed:
        return False,"Choose one of the available accent colors."
    with connect() as c:
        c.execute("""UPDATE users SET display_name=?,role=?,bio=?,accent_color=?,weekly_goal=?,
        accuracy_weight=?,relevance_weight=?,clarity_weight=?,completeness_weight=? WHERE id=?""",
        (display_name.strip(),role.strip(),bio.strip(),accent_color,int(weekly_goal),*weights,user_id))
    return True,"Workspace preferences saved."
