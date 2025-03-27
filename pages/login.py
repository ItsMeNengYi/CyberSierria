import streamlit as st
from auth import auth
from database import database

def main():
    if auth.username:
        st.title(f"Already logged in as {auth.username}.")
        st.write("Please logout to login as a different user.")
        return 
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')


    if st.button("Login"):
        if username and password:
            if auth.login(username, password) and database.login(username, password):
                st.success("Logged in successfully!")
                database.encrypt_user_data()
                st.rerun()
            else:
                st.error("Invalid username or password.")
        else:
            st.error("Please enter both username and password.")

if __name__ == "__main__":
    main()