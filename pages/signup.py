import streamlit as st
from auth import auth
from database import database
from zxcvbn import zxcvbn

def main():
    st.title("Create a New Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    # Display score of the password
    if password:
        result = zxcvbn(password)
        st.write(f"Password strength: {result['score']}/4")
        st.write(f"Suggestions: {result['feedback']['suggestions']}")
    openai_api_key = st.text_input("OpenAI API Key", type='password')
    pandasai_api_key = st.text_input("PandasAI API Key", type='password')


    if st.button("Sign Up"):
        if password and (result:=zxcvbn(password))['score'] < 3:
            st.error(f"Password is too weak. {result['feedback']['suggestions']}")
        elif username and password and (openai_api_key or pandasai_api_key):
            if auth.signup(username, password):
                st.success("Account created successfully!")
                st.write("Please login to access the chatbot.")
                database.create_new_user(username, password, openai_api_key, pandasai_api_key)
            else:
                st.error("Username already exists.")
        else:
            st.error("Please enter both username and password and one of the key.")

if __name__ == "__main__":
    main()