
import os
import re
import hashlib
import hmac
import secrets
from datetime import datetime

import streamlit as st
from supabase import create_client

_supabase = None


def get_db():
    global _supabase

    if _supabase is None:
        url = st.secrets.get(
            "SUPABASE_URL",
            os.environ.get("SUPABASE_URL", "")
        )
        key = st.secrets.get(
            "SUPABASE_KEY",
            os.environ.get("SUPABASE_KEY", "")
        )

        if not url or not key:
            raise RuntimeError(
                "Supabase credentials are missing. "
                "Check your Streamlit secrets."
            )

        _supabase = create_client(url, key)

    return _supabase


def init_db():
    get_db().table("users").select("id").limit(1).execute()


def _hash(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, 310000
    )
    return salt.hex() + ":" + digest.hex()


def _verify(password, stored):
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt_hex),
            310000
        )
        return hmac.compare_digest(actual.hex(), digest_hex)
    except Exception:
        return False


def create_user(username, email, password):
    username = (username or "").strip().lower()
    email = (email or "").strip().lower()

    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", username):
        return False, "Username must be 3–32 characters and use only letters, numbers, dots, underscores or hyphens."

    if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Enter a valid email address."

    if not isinstance(password, str) or not 8 <= len(password) <= 128:
        return False, "Password must contain 8–128 characters."

    try:
        get_db().table("users").insert({
            "username": username,
            "email": email,
            "password_hash": _hash(password),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }).execute()

        return True, "Account created."

    except Exception as e:
        message = str(e).lower()

        if "username" in message:
            return False, "That username is already registered."
        if "email" in message:
            return False, "That email address is already registered."
        if "duplicate" in message or "23505" in message:
            return False, "That username or email is already registered."

        return False, "Unable to create account. Please try again."


def authenticate_user(identity, password):
    identity = (identity or "").strip().lower()

    if not identity or not isinstance(password, str):
        return None

    db = get_db()

    result = db.table("users").select("*").eq(
        "username", identity
    ).limit(1).execute()

    if not result.data:
        result = db.table("users").select("*").eq(
            "email", identity
        ).limit(1).execute()

    if result.data:
        row = result.data[0]
        if _verify(password, row["password_hash"]):
            return row

    return None


def get_user(user_id):
    result = get_db().table("users").select(
        "id,username,email,created_at,display_name,role,bio,"
        "accent_color,weekly_goal,accuracy_weight,relevance_weight,"
        "clarity_weight,completeness_weight"
    ).eq("id", user_id).limit(1).execute()

    return result.data[0] if result.data else None


def update_profile(user_id, email):
    email = (email or "").strip().lower()

    if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Enter a valid email address."

    try:
        get_db().table("users").update({
            "email": email
        }).eq("id", user_id).execute()

        return True, "Email updated."

    except Exception as e:
        if "duplicate" in str(e).lower() or "23505" in str(e):
            return False, "That email is already in use."

        return False, "Unable to update email."


def save_evaluation(user_id, question, answer, result, model_name="Manual evaluation"):
    get_db().table("evaluations").insert({
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "accuracy": result["accuracy"],
        "relevance": result["relevance"],
        "clarity": result["clarity"],
        "completeness": result["completeness"],
        "overall_score": result["overall_score"],
        "strengths": result.get("strengths", ""),
        "weaknesses": result.get("weaknesses", ""),
        "improvements": result.get("improvements", ""),
        "verdict": result.get("verdict", ""),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model_name": model_name
    }).execute()


def get_history(user_id):
    result = get_db().table("evaluations").select(
        "id,question,answer,accuracy,relevance,clarity,completeness,"
        "overall_score,strengths,weaknesses,improvements,verdict,"
        "created_at,model_name"
    ).eq("user_id", user_id).order(
        "id", desc=True
    ).execute()

    return [
        tuple(row.get(column) for column in [
            "id", "question", "answer", "accuracy", "relevance",
            "clarity", "completeness", "overall_score", "strengths",
            "weaknesses", "improvements", "verdict", "created_at",
            "model_name"
        ])
        for row in result.data
    ]


def delete_evaluation(user_id, evaluation_id):
    get_db().table("evaluations").delete().eq(
        "id", evaluation_id
    ).eq("user_id", user_id).execute()


def update_preferences(
    user_id, display_name, role, bio, accent_color, weekly_goal,
    accuracy_weight, relevance_weight, clarity_weight,
    completeness_weight
):
    weights = [
        float(accuracy_weight),
        float(relevance_weight),
        float(clarity_weight),
        float(completeness_weight)
    ]

    if any(w < 0 or w > 100 for w in weights) or sum(weights) <= 0:
        return False, "Rubric weights must be between 0 and 100, with a non-zero total."

    if not 1 <= int(weekly_goal) <= 500:
        return False, "Weekly goal must be between 1 and 500."

    if len(display_name.strip()) > 60 or len(role.strip()) > 60 or len(bio.strip()) > 240:
        return False, "Please keep profile fields within their character limits."

    allowed = {"#8B5CF6", "#36C8F4", "#35D6A0", "#F2B85B", "#F472B6"}

    if accent_color not in allowed:
        return False, "Choose one of the available accent colors."

    get_db().table("users").update({
        "display_name": display_name.strip(),
        "role": role.strip(),
        "bio": bio.strip(),
        "accent_color": accent_color,
        "weekly_goal": int(weekly_goal),
        "accuracy_weight": weights[0],
        "relevance_weight": weights[1],
        "clarity_weight": weights[2],
        "completeness_weight": weights[3]
    }).eq("id", user_id).execute()

    return True, "Workspace preferences saved."
