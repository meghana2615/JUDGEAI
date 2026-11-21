
import os
import re
from datetime import datetime

import streamlit as st
from supabase import create_client

_supabase = None

def get_auth_client():
    url = st.secrets.get(
        "SUPABASE_URL",
        os.environ.get("SUPABASE_URL", "")
    )
    key = st.secrets.get(
        "SUPABASE_PUBLISHABLE_KEY",
        os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
    )

    if not url or not key:
        raise RuntimeError("Supabase authentication configuration is missing.")

    return create_client(url, key)


def get_admin_db():
    url = st.secrets.get(
        "SUPABASE_URL",
        os.environ.get("SUPABASE_URL", "")
    )
    key = st.secrets.get(
        "SUPABASE_KEY",
        os.environ.get("SUPABASE_KEY", "")
    )

    if not url or not key:
        raise RuntimeError("Supabase admin configuration is missing.")

    return create_client(url, key)

def get_user_db():
    access_token = st.session_state.get("auth_access_token")
    refresh_token = st.session_state.get("auth_refresh_token")

    if not access_token or not refresh_token:
        raise RuntimeError("Your session has expired. Please sign in again.")

    try:
        client = get_auth_client()
        client.auth.set_session(access_token, refresh_token)

        session = client.auth.get_session()

        if not session:
            raise RuntimeError("Unable to restore your authentication session.")

        st.session_state["auth_access_token"] = session.access_token
        st.session_state["auth_refresh_token"] = session.refresh_token

        return client

    except Exception as e:
        st.session_state.pop("auth_access_token", None)
        st.session_state.pop("auth_refresh_token", None)
        st.session_state.pop("auth_user_uuid", None)

        raise RuntimeError(
            "Your session has expired. Please sign in again."
        ) from e



def init_db():
    get_admin_db().table("users").select("id").limit(1).execute()





def create_user(username, email, password):
    username = (username or "").strip().lower()
    email = (email or "").strip().lower()

    if not re.fullmatch(r"[a-zA-Z0-9_.-]{3,32}", username):
        return False, "Username must be 3–32 characters and use only letters, numbers, dots, underscores or hyphens."

    if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Enter a valid email address."

    if not isinstance(password, str) or not 8 <= len(password) <= 128:
        return False, "Password must contain 8–128 characters."

    try:
        admin = get_admin_db()

        existing_username = admin.table("users").select(
            "id, username, email, auth_user_id"
        ).eq("username", username).limit(1).execute()

        if existing_username.data:
            profile = existing_username.data[0]

            if profile["email"].lower() != email:
                return False, "That username is already registered."

            if profile.get("auth_user_id"):
                return False, "This account is already registered. Please sign in."

        existing_email = admin.table("users").select(
            "id, username, email, auth_user_id"
        ).eq("email", email).limit(1).execute()

        if existing_email.data:
            profile = existing_email.data[0]

            if profile["username"].lower() != username:
                return False, "This email is already associated with another username."

            if profile.get("auth_user_id"):
                return False, "This account is already registered. Please sign in."

        response = get_auth_client().auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"username": username}
            }
        })

        auth_user = response.user

        if not auth_user:
            return False, "Unable to create account. Please try again."

        if auth_user.identities is not None and len(auth_user.identities) == 0:
            return False, "This email is already registered. Please sign in."

        existing_profile = (
            existing_username.data[0]
            if existing_username.data
            else existing_email.data[0] if existing_email.data
            else None
        )

        if existing_profile:
            admin.table("users").update({
                "auth_user_id": str(auth_user.id)
            }).eq("id", existing_profile["id"]).execute()
        else:
            admin.table("users").insert({
                "username": username,
                "email": email,
                "auth_user_id": str(auth_user.id),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }).execute()

        return True, "Account created. Please check your email and verify your address before signing in."

    except Exception as e:
        message = str(e).lower()

        if "duplicate" in message or "23505" in message:
            return False, "That username or email is already registered."

        return False, "Unable to create account. Please try again."



def authenticate_user(identity, password):
    identity = (identity or "").strip().lower()

    if not identity or not isinstance(password, str) or not password:
        return None

    try:
        admin = get_admin_db()

        result = admin.table("users").select(
            "id,username,email,auth_user_id"
        ).eq("username", identity).limit(1).execute()

        if not result.data:
            result = admin.table("users").select(
                "id,username,email,auth_user_id"
            ).eq("email", identity).limit(1).execute()

        if not result.data:
            return None

        profile = result.data[0]

        response = get_auth_client().auth.sign_in_with_password({
            "email": profile["email"],
            "password": password
        })

        session = response.session
        auth_user = response.user

        if not session or not auth_user:
            return None

        verified = (
            getattr(auth_user, "email_confirmed_at", None)
            or getattr(auth_user, "confirmed_at", None)
        )

        if not verified:
            return None

        auth_user_id = str(auth_user.id)

        if profile.get("auth_user_id") and profile["auth_user_id"] != auth_user_id:
            return None

        if not profile.get("auth_user_id"):
            admin.table("users").update({
                "auth_user_id": auth_user_id
            }).eq("id", profile["id"]).execute()

        admin.table("evaluations").update({
            "auth_user_id": auth_user_id
            }).eq("user_id", profile["id"]).execute()

        st.session_state["auth_access_token"] = session.access_token
        st.session_state["auth_refresh_token"] = session.refresh_token
        st.session_state["auth_user_uuid"] = auth_user_id

        return profile

    except Exception:
        return None



def get_user(user_id):
    auth_user_id = st.session_state.get("auth_user_uuid")

    if not auth_user_id:
        return None

    try:
        result = get_user_db().table("users").select(
            "id,username,email,created_at,display_name,role,bio,"
            "accent_color,weekly_goal,accuracy_weight,relevance_weight,"
            "clarity_weight,completeness_weight"
        ).eq("auth_user_id", auth_user_id).eq(
            "id", user_id
        ).limit(1).execute()

        return result.data[0] if result.data else None

    except Exception:
        return None



def update_profile(user_id, email):
    email = (email or "").strip().lower()

    if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Enter a valid email address."

    auth_user_id = st.session_state.get("auth_user_uuid")

    if not auth_user_id:
        return False, "Please sign in again."

    try:
        result = get_user_db().auth.update_user({
            "email": email
        })

        if not result.user:
            return False, "Unable to request the email change."

        return True, "A confirmation email has been sent. Confirm the new address to complete the change."

    except Exception as e:
        message = str(e).lower()

        if "already" in message or "duplicate" in message:
            return False, "That email address is already in use."

        return False, "Unable to update email. Please try again."


def save_evaluation(user_id, question, answer, result, model_name="Manual evaluation"):
    auth_user_id = st.session_state.get("auth_user_uuid")

    if not auth_user_id:
        raise RuntimeError("Please sign in again before saving an evaluation.")

    get_user_db().table("evaluations").insert({
        "user_id": user_id,
        "auth_user_id": auth_user_id,
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
    auth_user_id = st.session_state.get("auth_user_uuid")

    if not auth_user_id:
        return []

    try:
        result = get_user_db().table("evaluations").select(
            "id,question,answer,accuracy,relevance,clarity,completeness,"
            "overall_score,strengths,weaknesses,improvements,verdict,"
            "created_at,model_name"
        ).eq("user_id", user_id).eq(
            "auth_user_id", auth_user_id
        ).order("id", desc=True).execute()

        return [
            tuple(row.get(column) for column in [
                "id", "question", "answer", "accuracy", "relevance",
                "clarity", "completeness", "overall_score", "strengths",
                "weaknesses", "improvements", "verdict", "created_at",
                "model_name"
            ])
            for row in result.data
        ]

    except Exception:
        return []



def delete_evaluation(user_id, evaluation_id):
    auth_user_id = st.session_state.get("auth_user_uuid")

    if not auth_user_id:
        raise RuntimeError("Please sign in again before deleting an evaluation.")

    get_user_db().table("evaluations").delete().eq(
        "id", evaluation_id
    ).eq(
        "user_id", user_id
    ).eq(
        "auth_user_id", auth_user_id
    ).execute()


def update_preferences(
    user_id, display_name, role, bio, accent_color, weekly_goal,
    accuracy_weight, relevance_weight, clarity_weight,
    completeness_weight
):
    auth_user_id = st.session_state.get("auth_user_uuid")

    if not auth_user_id:
        return False, "Please sign in again."

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

    try:
        get_user_db().table("users").update({
            "display_name": display_name.strip(),
            "role": role.strip(),
            "bio": bio.strip(),
            "accent_color": accent_color,
            "weekly_goal": int(weekly_goal),
            "accuracy_weight": weights[0],
            "relevance_weight": weights[1],
            "clarity_weight": weights[2],
            "completeness_weight": weights[3]
        }).eq("id", user_id).eq(
            "auth_user_id", auth_user_id
        ).execute()

        return True, "Workspace preferences saved."

    except Exception:
        return False, "Unable to save workspace preferences."
