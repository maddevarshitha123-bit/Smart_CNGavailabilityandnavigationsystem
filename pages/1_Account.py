import streamlit as st
from utils.ui import setup_page, header
from utils import auth, database as db

setup_page("Account", "👤")
header("Account", "Login, register and manage your profile")

user = auth.current_user()
try:
    if user:
        st.subheader("Your profile")
        st.write(f"**Name:** {user['name']}  \n**Email:** {user['email']}  \n**Role:** {user['role']}")
        with st.form("profile"):
            new_name = st.text_input("Update name", value=user["name"])
            if st.form_submit_button("Save name"):
                if len(new_name.strip()) < 2:
                    st.error("Name is too short.")
                else:
                    db.update_user_name(user["user_id"], new_name.strip())
                    st.session_state["user"]["name"] = new_name.strip()
                    st.success("Name updated.")
        with st.form("pwd"):
            old = st.text_input("Current password", type="password")
            new = st.text_input("New password", type="password")
            if st.form_submit_button("Change password"):
                row = db.get_user_by_email(user["email"])
                problems = auth.validate_password(new)
                if not auth.verify_password(old, row["password_hash"]):
                    st.error("Current password is wrong.")
                elif problems:
                    st.error("New password needs: " + ", ".join(problems) + ".")
                else:
                    db.update_password(user["user_id"], auth.hash_password(new))
                    st.success("Password changed.")
        if st.button("Logout", key="logout_main"):
            auth.logout(); st.rerun()
    else:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            with st.form("login"):
                email = st.text_input("Email")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    ok, msg = auth.login_user(email, pw)
                    (st.success if ok else st.error)(msg)
                    if ok: st.rerun()
        with tab2:
            with st.form("register"):
                name = st.text_input("Full name")
                email_r = st.text_input("Email", key="reg_email")
                pw_r = st.text_input("Password", type="password", key="reg_pw",
                                     help="8+ chars with upper, lower, digit and special character")
                if st.form_submit_button("Register"):
                    ok, msg = auth.register_user(name, email_r, pw_r)
                    (st.success if ok else st.error)(msg)
except db.DatabaseError as e:
    st.error(f"Database problem: {e}")
