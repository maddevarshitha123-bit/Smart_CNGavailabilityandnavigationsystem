"""Registration, login, password hashing and access control."""
import re
import bcrypt
import streamlit as st
from utils import database as db

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


def validate_email(email):
    return bool(email) and len(email) <= 150 and EMAIL_RE.match(email) is not None


def validate_password(pw):
    """Return a list of problems (empty list = password is fine)."""
    problems = []
    if len(pw or "") < 8: problems.append("at least 8 characters")
    if not re.search(r"[A-Z]", pw or ""): problems.append("one uppercase letter")
    if not re.search(r"[a-z]", pw or ""): problems.append("one lowercase letter")
    if not re.search(r"\d", pw or ""): problems.append("one digit")
    if not re.search(r"[^\w\s]", pw or ""): problems.append("one special character")
    return problems


def hash_password(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def verify_password(pw, hashed):
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except (ValueError, AttributeError):
        return False


def register_user(name, email, password):
    """Returns (ok, message)."""
    name, email = (name or "").strip(), (email or "").strip().lower()
    if len(name) < 2: return False, "Please enter your name."
    if not validate_email(email): return False, "Please enter a valid email address."
    problems = validate_password(password)
    if problems: return False, "Password needs: " + ", ".join(problems) + "."
    if db.get_user_by_email(email): return False, "This email is already registered."
    db.create_user(name, email, hash_password(password))
    return True, "Registration successful. You can now log in."


def login_user(email, password):
    """Returns (ok, message). Same message for wrong email/password (no info leak)."""
    email = (email or "").strip().lower()
    if not validate_email(email) or not password:
        return False, "Invalid email or password."
    user = db.get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return False, "Invalid email or password."
    st.session_state["user"] = {"user_id": user["user_id"], "name": user["name"],
                                "email": user["email"], "role": user["role"]}
    return True, f"Welcome, {user['name']}!"


def logout():
    st.session_state.pop("user", None)


def current_user():
    return st.session_state.get("user")


def require_login():
    if not current_user():
        st.warning("Please log in from the Account page to use this feature.")
        st.stop()


def require_admin():
    require_login()
    if current_user()["role"] != "admin":
        st.error("Access denied: administrators only.")
        st.stop()
