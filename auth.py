import os
from Cryptodome.Hash import SHA256, SHA3_512
import pickle
import cryptography.fernet, struct
import base64
import shutil

class Auth():
    _instance = None  # Static variable to hold the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Auth, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  
            self.username = None
            self.password = None
            self.is_logged_in = False
            self.initialized = True
    def logout(self):
        self.username = None
        self.password = None
        self.is_logged_in = False

    def encrypt_password(self, password):
        hash_obj = SHA3_512.new()
        hash_obj.update(password.encode())
        return hash_obj.hexdigest()

    def get_username(self):
        return self.username
    
    def load_users(self):
        if os.path.exists("users.pkl") and os.path.getsize("users.pkl") > 0:
            with open("users.pkl", "rb") as file:
                return pickle.load(file)
        else:
            return {}

    def save_users(self, users):
        with open("users.pkl", "wb") as file:
            pickle.dump(users, file)

    def signup(self, username, password):
        users = self.load_users()
        
        if username in users:
            return False 
        
        encrypted_password = self.encrypt_password(password)
        users[username] = encrypted_password
        self.save_users(users)
        return True

    def login(self, username, password):
        users = self.load_users()

        if username in users:
            encrypted_password = users[username]

            # Check if the password has same hash value
            if encrypted_password == self.encrypt_password(password):
                self.username = username
                self.password = password
                self.is_logged_in = True
                return True 
        return False 

    def pad(self, data):
        padding_length = 16 - len(data) % 16
        padding = bytes([padding_length] * padding_length)
        return data + padding

    def unpad(self, data):
        padding_length = data[-1]
        if padding_length < 1 or padding_length > 16:
            raise ValueError("Invalid padding encountered")
        return data[:-padding_length]

    def encrypt_file(self, password, input_path, output_path = None, block = 1 << 16):
        if not os.path.exists(input_path):
            return False
        hash_obj = SHA256.new()
        hash_obj.update(password.encode())
        key = base64.urlsafe_b64encode(hash_obj.digest())
        fernet = cryptography.fernet.Fernet(key)

        if output_path is None:
            output_path = input_path.split(".")[0] + "_encrypted." + input_path.split(".")[1]
        with open(input_path, 'rb') as fi, open(output_path, 'wb') as fo:
            while True:
                chunk = fi.read(block)
                if len(chunk) == 0:
                    break
                enc = fernet.encrypt(chunk)
                fo.write(struct.pack('<I', len(enc)))
                fo.write(enc)
                if len(chunk) < block:
                    break

        # Remove the original file
        os.remove(input_path)
        return True

    def decrypt_file(self, password, output_path, input_path = None):
        hash_obj = SHA256.new()
        hash_obj.update(password.encode())
        key = base64.urlsafe_b64encode(hash_obj.digest())
        fernet = cryptography.fernet.Fernet(key)
        if input_path is None:
            input_path = output_path.split(".")[0] + "_encrypted." + output_path.split(".")[1]
        output_path = output_path
        with open(input_path, 'rb') as fi, open(output_path, 'wb') as fo:
            while True:
                size_data = fi.read(4)
                if len(size_data) == 0:
                    break
                chunk = fi.read(struct.unpack('<I', size_data)[0])
                dec = fernet.decrypt(chunk)
                fo.write(dec)
        # Remove the encrypted file
        os.remove(input_path)
        return True
    
    def zip_and_encrypt_folder(self, password, folder_path):
        if not os.path.exists(folder_path):
            return False
        shutil.make_archive(folder_path, 'zip', folder_path)
        shutil.rmtree(folder_path, ignore_errors=False)
        self.encrypt_file(password, folder_path + ".zip")
        return True

    def decrypt_and_unzip_folder(self, password, folder_path):
        if os.path.exists(folder_path):
            return True
        input_path = folder_path.split(".")[0] + "_encrypted." + folder_path.split(".")[1]
        if not os.path.exists(input_path):
            return False
        
        self.decrypt_file(password,input_path= input_path, output_path=folder_path)
        shutil.unpack_archive(folder_path, folder_path.split(".")[0])
        os.remove(folder_path)
        return True
        
auth = Auth()

