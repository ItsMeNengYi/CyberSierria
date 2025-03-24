from dotenv import load_dotenv
import streamlit as st
import os
import pandasai as pdai
import pandas as pd
from pandasai_openai import OpenAI

# Load the API KEY 
load_dotenv() 
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Create directory for the data
if not os.path.exists("data"):
    os.makedirs("data")

# Setup variables
dfs = [] # Dataframe
llm = OpenAI(api_token=OPENAI_API_KEY) # OpenAI model
pdai.config.set({"llm": llm})
num_of_rows = 1

# Titles
st.title("CyberSierra Chatbot")
st.caption("powered by OpenAI")

# File Uploader
uploaded_files = st.file_uploader(type=["csv", "xls"],accept_multiple_files=True, label="Upload a csv")
if uploaded_files is not None:
    for file in uploaded_files:
        # Save the file under the data directory
        with open(os.path.join("data", file.name), "wb") as f:
            f.write(file.getbuffer())
        
        # Load the data into dataframe
        if file.name.endswith(".xls"):
            df = pd.read_excel(os.path.join("data", file.name))
        else:
            df = pd.read_csv(os.path.join("data", file.name))

# Display the dataframe
if len(dfs) > 0:
    num_of_rows = st.number_input("Show how many rows?", min_value=1)
    first_n_rows = df.head(num_of_rows)
    st.dataframe(data=first_n_rows, use_container_width=True)

# Chatbot
if "messages" not in st.session_state:
    display_message = ""
    if len(dfs) == 0:
        display_message = "Please upload a csv to get started."
    else:
        display_message = "What would you like to know about this data?"
    st.session_state["messages"] = [{"role": "assistant", "content": display_message}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Data selector
if len(dfs) > 0:
    selected_data = st.selectbox("Select the data", df)

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)   

    if len(dfs) == 0:
        st.chat_message("assistant").write("Please upload a csv to get started.")
    else:
        # sdf = pdai.SmartDataframe(df)
        # response = sdf.chat(prompt)
        response = "balabala"
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(msg)