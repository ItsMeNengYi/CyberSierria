import streamlit as st
from auth import auth

st.set_page_config(page_title="CyberSierra Chatbot", page_icon=":robot_face:")

if auth.is_logged_in:
    st.title(f"Welcome back to CyberSierra Chatbot! {auth.username}")
    st.write("You can start chatting now.")
    st.write("Please make sure to logout before closing the browser.")
else:
    st.title("Welcome to CyberSierra Chatbot!")
    st.write("Please login to access the chatbot.")

