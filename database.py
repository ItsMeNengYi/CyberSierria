import os
import json
import pandas as pd

# Database that store chat history graph and dataframes
class Database():
    def __init__(self):
        self.all_datas = []
        self.base_path = "database/"
        self.num_of_history_chat = 0
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

        # load all the data
        for chat_folder in os.listdir(self.base_path):
            data = open(self.base_path + chat_folder + "/data.json", "r").read()
            if data != "":
                self.all_datas.append(json.loads(data))
                self.num_of_history_chat += 1
        self.current_chat_id = max(0, len(self.all_datas) - 1)
        self.new_chat()

    def get_saved_file_path(self):
        return self.base_path + "chat_" + str(self.current_chat_id) + "/files/"

    def get_dataframes_path(self):
        return self.base_path + "chat_" + str(self.current_chat_id) + "/dataframes/"
    
    def get_data_json_path(self):
        return self.base_path + "chat_" + str(self.current_chat_id) + "/data.json"
    
    def save_dataframe(self, df):
        # Save the dataframe under the chat folder
        df_path = self.get_dataframes_path() + "df_" + str(len(os.listdir(self.get_dataframes_path()))) + ".csv"
        df.to_csv(df_path, index=False)
        return df_path
    
    def save(self, dfs, selected_df, messages):
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

    def load(self):
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
        return None, None, None
    
    def switch_chat(self, chat_id):
        self.current_chat_id = chat_id

    def new_chat(self):
        if len(self.all_datas) != 0 and len(self.all_datas[-1]["messages"]) == 1:
            self.current_chat_id = len(self.all_datas) - 1
            return
        # Update variables
        self.num_of_history_chat += 1
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
