from dotenv import load_dotenv
import streamlit as st
import os
import pandasai as pdai
import pandas as pd
from pandasai_openai import OpenAI
from database import database
from auth import auth

def main():
    # Load the API KEY 
    global database
    if (env_path := database.get_env_path(auth.username)) is not None:
        load_dotenv(env_path) 
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
        PANDASAI_API_KEY = os.environ.get("PANDASAI_API_KEY", "")
    else:
        OPENAI_API_KEY = ""
        PANDASAI_API_KEY = ""
    if OPENAI_API_KEY == "" and PANDASAI_API_KEY == "":
        st.error("API Key not found. Please make sure you have logged in and upload the .env file.")
        return
    
    # Setup variables
    if "dfs" not in st.session_state: # {<path> : Dataframe}
        st.session_state["dfs"] = {}
    if "selected_df" not in st.session_state:
        st.session_state["selected_df"] = None # {path : dataframe}
    if "num_of_rows" not in st.session_state:
        st.session_state.num_of_rows = 1
    if "database" not in st.session_state:
        st.session_state["database"] = database
    dfs = st.session_state["dfs"]
    selected_df = st.session_state["selected_df"]
    num_of_rows = st.session_state["num_of_rows"]
    database = st.session_state["database"]

    if "messages" not in st.session_state:
        display_message = ""
        if len(dfs) == 0:
            display_message = "Please upload a csv to get started."
        else:
            display_message = "What would you like to know about this data?"
        st.session_state["messages"] = [{"role": "assistant", "content": display_message}]

    # Load the data
    temp_dfs, temp_selected_df, temp_messages = database.load()
    if temp_dfs is not None:
        dfs = temp_dfs
    if temp_selected_df is not None:
        selected_df = temp_selected_df
    if temp_messages is not None:
        st.session_state["messages"] = temp_messages

    # PandasAI Setup
    if OPENAI_API_KEY != "":
        llm = OpenAI(api_token=OPENAI_API_KEY) # OpenAI model
        pdai.config.set({"llm": llm})
    elif PANDASAI_API_KEY != "":
        pdai.api_key.set(PANDASAI_API_KEY)

    # Redirect generated charts to the database folder
    # pdai.config.set({"save_charts_path" : database.get_exports_path()})

    # Sidebar with buttons to logout, view chat history and create new chat

    if (logout := st.sidebar.button("Logout")):
        database.save(dfs, selected_df, st.session_state["messages"])
        database.logout()
        auth.logout()
        st.rerun()
    
    if (new_chat := st.sidebar.button("New Chat")):
        # Save the current chat
        database.save(dfs, selected_df, st.session_state["messages"])
        database.new_chat()

        # Load the chat
        dfs, selected_df, st.session_state["messages"] = database.load()
        st.rerun()


    for i in range(database.num_of_history_chat - 1, -1, -1):
        if (load_chat := st.sidebar.button("Load Chat " + str(i), icon="🔥" if database.current_chat_id == i else None)):
            # Save the current chat
            database.save(dfs, selected_df, st.session_state["messages"])

            # Load the chat
            database.switch_chat(i)
            dfs, selected_df, st.session_state["messages"] = database.load()
            st.rerun()

    # Titles
    st.title("CyberSierra Chatbot")
    st.caption("powered by OpenAI and PandasAI")


    # File Uploader
    uploaded_files = st.file_uploader(type=["csv", "xls"], accept_multiple_files=True, label="Upload csv or xls files")
    if uploaded_files is not None:
        for file in uploaded_files:
            # Save the file in data folder
            files_folder_path = database.get_saved_file_path()
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
                path = database.save_dataframe(df)
                res = {"role": "assistant", "type": "dataframe", "content": path}
            elif t == "chart" or t == "plot":
                path = response.value[index]
                res = {"role": "assistant", "type": "plot", "content": path}
            else:
                res =  {"role": "assistant", "content": str(response.value[index])}
            st.session_state.messages.append(res)

    # Displaying Message
    for i,msg in enumerate(st.session_state.messages):
        if msg["role"] == "assistant":
            # message and feedback
            col1, col2 = st.columns([4, 1])
            with col1:
                if len(dfs) > 0 and "type" not in msg and msg["content"] == "Please upload a csv to get started.":
                    continue
                if "type" in msg:
                    if msg["type"] == "dataframe":
                        st.chat_message(msg["role"]).write("Displaying the dataframe")
                        st.chat_message(msg["role"]).write(pd.read_csv(msg["content"]))
                    elif msg["type"] == "plot":
                        st.chat_message(msg["role"]).write("Displaying the plot")
                        st.image(msg["content"])
                    else:
                        st.chat_message(msg["role"]).write(msg["content"])
                else:
                    st.chat_message(msg["role"]).write(msg["content"])
            with col2:
                if "feedback" in msg:
                    if msg["feedback"] == "positive":
                        st.button("👍", disabled=True, key=f"thumbs_up_{i}")
                    elif msg["feedback"] == "negative":
                        st.button("👎", disabled=True, key=f"thumbs_down_{i}")
                else:
                    if st.button("👍", key=f"like_{i}"):
                        msg["feedback"] = "positive"
                        st.rerun()
                    if st.button("👎", key=f"dislike_{i}"):
                        msg["feedback"] = "negative"
                        st.rerun()
        else:
            st.chat_message(msg["role"]).write(msg["content"])

    # Process prompts
    if prompt := st.chat_input("Ask a question about " + (str(selected_df[0]) if  selected_df is not None else "") + " data"):
        # Store & Display User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message(st.session_state.messages[-1]["role"]).write(st.session_state.messages[-1]["content"])

        # Store & Display Assistant Response
        if selected_df is not None:
            sdf = pdai.SmartDataframe(list(selected_df)[1])
            response = parse_and_save(sdf.chat(prompt))
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Please upload a csv to get started."})

        # Update the chatbot response
        st.rerun()

    # Save the data
    if len(dfs) > 0:
        database.save(dfs,selected_df,st.session_state["messages"])
    database.encrypt_user_data()

if __name__ == "__main__":
    main()