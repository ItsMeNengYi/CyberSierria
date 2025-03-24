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
dfs = {} # {path : Dataframe}
selected_df = None # Selected dataframe
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
        path = os.path.join("data", file.name)
        # Load the data into dataframe
        if file.name.endswith(".xls"):
            dfs.update({file.name : pd.read_excel(path)})
        else:
            dfs.update({file.name : pd.read_csv(path)})
    if len(dfs) > 0 and selected_df is None:
        selected_df = next(iter(dfs.items()))

# Display the dataframe
if selected_df is not None:
    # Layout for selector & input
    col1, col2 = st.columns([1, 3]) 

    with col1:
        num_of_rows = st.number_input("Show how many rows?", min_value=1)

    with col2:
        options = list(dfs.keys())
        option = st.selectbox("Data Selected", options)
        if option:
            selected_df = (option, dfs[option])
    first_n_rows = selected_df[1].head(num_of_rows)
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

if prompt := st.chat_input("Ask a question about the data"):
    # Store & Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Store & Display Assistant Response
    if selected_df is not None:
        # sdf = pdai.SmartDataframe(selected_df)
        # response = sdf.ask(prompt)
        response = "asdf"
    else:
        response = "Please upload a csv to get started."
    st.session_state.messages.append({"role": "assistant", "content": response})
    # Update the chatbot response
    st.rerun()