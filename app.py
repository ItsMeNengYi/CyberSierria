from dotenv import load_dotenv
import streamlit as st
import os
import pandasai as pdai
import pandas as pd
from pandasai_openai import OpenAI

# Load the API KEY 
load_dotenv() 
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
PANDASAI_API_KEY = os.environ.get("PANDASAI_API_KEY", "")

# Create directory for the data
if not os.path.exists("data"):
    os.makedirs("data")

# Setup variables
dfs = {} # {path : Dataframe}
selected_df = None # Selected {path : dataframe}
num_of_rows = 1
if "messages" not in st.session_state:
    display_message = ""
    if len(dfs) == 0:
        display_message = "Please upload a csv to get started."
    else:
        display_message = "What would you like to know about this data?"
    st.session_state["messages"] = [{"role": "assistant", "content": display_message}]

# Choose LLM
if OPENAI_API_KEY != "":
    llm = OpenAI(api_token=OPENAI_API_KEY) # OpenAI model
    pdai.config.set({"llm": llm})
else:
    pdai.api_key.set(PANDASAI_API_KEY)

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

# response parser
def parse_and_save(response):

    if not isinstance(response.type, list):
        response.type = [response.type]
        response.value = [response.value]

    for index,t in enumerate(response.type):
        if t == 'dataframe':
            df = response.value[index]
            res = {"role": "assistant", "type": "dataframe", "content": df}
        elif t == "chart" or "plot" or "graph":
            path = response.value[index]
            res = {"role": "assistant", "type": "plot", "content": path}
        else:
            print("this is "+ t)
            res =  {"role": "assistant", "content": response.value[index]}
        st.session_state.messages.append(res)

# Displaying Message
for msg in st.session_state.messages:
    if len(dfs) > 0 and "type" not in msg and msg["content"] == "Please upload a csv to get started.":
        continue
    if "type" in msg:
        if msg["type"] == "dataframe":
            st.chat_message(msg["role"]).write("Displaying the dataframe")
            st.chat_message(msg["role"]).write(pd.DataFrame(msg["content"]))
        elif msg["type"] == "plot":
            st.chat_message(msg["role"]).write("Displaying the plot")
            st.image(msg["content"])
        else:
            st.chat_message(msg["role"]).write(msg["content"])
    else:
        st.chat_message(msg["role"]).write(msg["content"])

# Process prompts
if prompt := st.chat_input("Ask a question about " + (str(selected_df[0]) if  selected_df is not None else "") + " data"):
    # Store & Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message(st.session_state.messages[-1]["role"]).write(st.session_state.messages[-1]["content"])

    # Store & Display Assistant Response
    if selected_df is not None:
        sdf = pdai.SmartDataframe(selected_df[1])
        response = parse_and_save(sdf.chat(prompt))
    else:
        st.session_state.messages.append({"role": "assistant", "content": "Please upload a csv to get started."})

    # Update the chatbot response
    st.rerun()
