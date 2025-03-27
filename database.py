import os
import json
import pandas as pd
from auth import auth

# Database that store chat history graph and dataframes
class Database():
    def __init__(self):
        self.all_datas = []
        self.database_path = "database/"
        self.base_path = self.database_path
        self.current_chat_id = 0
    
    def logout(self):
        self.base_path = self.database_path
        self.current_chat_id = 0
        self.all_datas = []

    def move_to_user_database(self, path):
        dir_name = os.path.dirname(path)
        self.decrypt_user_data()

        # If the file is not exist
        if not os.path.exists(path):
            return None
        if not os.path.exists(self.base_path + dir_name):
            os.makedirs(self.base_path + dir_name)
        # Move the file to the user database
        os.rename(path, self.base_path + path)

        self.encrypt_user_data()
        return self.base_path + path

    def encrypt_user_data(self):
        auth.zip_and_encrypt_folder(auth.password, "".join(self.base_path[:-1]))

    def decrypt_user_data(self):
        auth.decrypt_and_unzip_folder(auth.password, self.base_path[:-1] + ".zip")

    def get_env_path(self, username):
        self.decrypt_user_data()
        if username is None:
            return None
        if os.path.exists("database/" + username + "/.env"):
            return "database/" + username + "/.env"
        return None

    def create_new_user(self, username, password, openai_api_key, pandasai_api_key):
        self.base_path = self.database_path + username + "/"
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            # Save the .env file
            with open(self.base_path + ".env", "w") as file:
                if openai_api_key:
                    file.write(f"OPENAI_API_KEY={openai_api_key}\n")
                if pandasai_api_key:
                    file.write(f"PANDASAI_API_KEY={pandasai_api_key}\n")
            # Create data.json
            self.new_chat()
            auth.zip_and_encrypt_folder(password, "".join(self.base_path[:-1]))

    def login(self, username, password):
        # Check if already decrypt folder
        already_decrypt_folder = os.path.exists(self.database_path + username)
        if  already_decrypt_folder or auth.decrypt_and_unzip_folder(password, self.database_path + username + ".zip"):
            self.base_path = self.database_path + username + "/"
            # load all the data
            self.load_all_files()
            self.current_chat_id = max(0, len(self.all_datas) - 1)
            return True
        return False

    def get_user_env_path(self):
        return self.base_path + ".env"

    def load_all_files(self):
        for chat_folder in os.listdir(self.base_path):
            if "chat" not in chat_folder:
                continue
            data = open(self.base_path + chat_folder + "/data.json", "r").read()
            if data != "":
                self.all_datas.append(json.loads(data))

    def get_saved_file_path(self):
        return self.base_path + "chat_" + str(self.current_chat_id) + "/files/"

    def get_dataframes_path(self):
        return self.base_path + "chat_" + str(self.current_chat_id) + "/dataframes/"
    
    def get_data_json_path(self):
        return self.base_path + "chat_" + str(self.current_chat_id) + "/data.json"
    
    def get_num_of_history_chat(self):
        return len(self.all_datas)
    
    def save_dataframe(self, df):
        # Save the dataframe under the chat folder
        df_path = self.get_dataframes_path() + "df_" + str(len(os.listdir(self.get_dataframes_path()))) + ".csv"
        df.to_csv(df_path, index=False)
        return df_path
    
    def save(self, dfs, selected_df, messages):
        self.decrypt_user_data()
        dfs_paths=list(dfs.keys())
        if selected_df is not None:
            selected_df_path = next(iter(selected_df)) 

        else:
            selected_df_path = None
        chat_id = self.current_chat_id
        for index, data in enumerate(self.all_datas):
            if data["id"] == chat_id:
                data["dfs_paths"] = dfs_paths
                data["selected_df_path"] = selected_df_path
                data["messages"] = messages
                break
        json.dump(self.all_datas[index], open(self.get_data_json_path(), "w"))

        self.encrypt_user_data()

    def load(self):
        self.decrypt_user_data()
        for data in self.all_datas:
            if data["id"] != self.current_chat_id:
                continue
            dfs_paths = data["dfs_paths"]
            selected_df_path = data["selected_df_path"]
            messages = data["messages"]
            dfs = {}
            selected_df = None
            for df_path in dfs_paths:
                full_path = self.get_saved_file_path() + df_path
                if df_path.split(".")[1] == "xls":
                    dfs.update({df_path : pd.read_excel(full_path)})
                else:
                    dfs.update({df_path : pd.read_csv(full_path)})
            if selected_df_path is not None:
                full_path = self.get_saved_file_path() + selected_df_path
                if selected_df_path.split(".")[1] == "xls":
                    selected_df = {selected_df_path : pd.read_excel(full_path)}
                else:
                    selected_df = {selected_df_path : pd.read_csv(full_path)}
            return dfs, selected_df, messages
        self.encrypt_user_data()
        return None, None, None
    
    def switch_chat(self, chat_id):
        self.current_chat_id = chat_id

    def new_chat(self):
        if len(self.all_datas) != 0 and len(self.all_datas[-1]["messages"]) == 1:
            self.current_chat_id = len(self.all_datas) - 1
            return
        # Update variables
        new_id = len(self.all_datas)
        self.all_datas.append({
            "id":new_id,
            "dfs_paths":[],
            "selected_df_path":None,
            "messages":[{"role": "assistant", "content": "Please upload a csv to get started."}]
        })
        self.current_chat_id = new_id

        # Create directory for the data and history chat
        if not os.path.exists(self.get_saved_file_path()):
            os.makedirs(self.get_saved_file_path())
        if not os.path.exists(self.get_dataframes_path()):
            os.makedirs(self.get_dataframes_path())
        json.dump(self.all_datas[new_id], open(self.get_data_json_path(), "w"))
    
    def get_current_chat_id(self):
        return self.current_chat_id

database = Database()