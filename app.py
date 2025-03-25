from dotenv import load_dotenv
import streamlit as st
import os
import pandasai as pdai
import pandas as pd
from pandasai_openai import OpenAI
from database import Database

# Load the API KEY 
load_dotenv() 
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
PANDASAI_API_KEY = os.environ.get("PANDASAI_API_KEY", "")

# Setup variables
dfs = {} # {path : Dataframe}
selected_df = None # Selected {path : dataframe}
num_of_rows = 1
if "database" not in st.session_state:
    st.session_state["database"] = Database()

if "messages" not in st.session_state:
    display_message = ""
    if len(dfs) == 0:
        display_message = "Please upload a csv to get started."
    else:
        display_message = "What would you like to know about this data?"
    st.session_state["messages"] = [{"role": "assistant", "content": display_message}]

# Load the data
dfs, selected_df, st.session_state["messages"] = st.session_state["database"].load()

# PandasAI Setup
if OPENAI_API_KEY != "":
    llm = OpenAI(api_token=OPENAI_API_KEY) # OpenAI model
    pdai.config.set({"llm": llm})
else:
    pdai.api_key.set(PANDASAI_API_KEY)

# Redirect generated charts to the database folder
# pdai.config.set({"save_charts_path" : st.session_state["database"].get_exports_path()})


# Titles
st.title("CyberSierra Chatbot")
st.caption("powered by OpenAI and PandasAI")

# File Uploader
uploaded_files = st.file_uploader(type=["csv", "xls"], accept_multiple_files=True, label="Upload csv or xls files")
if uploaded_files is not None:
    for file in uploaded_files:
        # Save the file in data folder
        files_folder_path = st.session_state["database"].get_saved_file_path()
        with open(os.path.join(files_folder_path, file.name), "wb") as f:
            f.write(file.getbuffer())
        path = os.path.join(files_folder_path, file.name)
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
            path = st.session_state["database"].save_dataframe(df)
            res = {"role": "assistant", "type": "dataframe", "content": path}
        elif t == "chart" or t == "plot":
            path = response.value[index]
            res = {"role": "assistant", "type": "plot", "content": path}
        else:
            res =  {"role": "assistant", "content": str(response.value[index])}
        st.session_state.messages.append(res)

# Displaying Message
for msg in st.session_state.messages:
    if len(dfs) > 0 and "type" not in msg and msg["content"] == "Please upload a csv to get started.":
        continue
    if "type" in msg:
        if msg["type"] == "dataframe":
            st.chat_message(msg["role"]).write("Displaying the dataframe")
            st.chat_message(msg["role"]).write(pd.read_csv(msg["content"]))
            continue
        elif msg["type"] == "plot":
            st.chat_message(msg["role"]).write("Displaying the plot")
            st.image(msg["content"])
            continue
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

# Save the data
if len(dfs) > 0:
    st.session_state["database"].save(dfs_paths=list(dfs.keys()),
                                    selected_df_path = selected_df[0] if selected_df is not None else None, 
                                    messages=st.session_state["messages"])