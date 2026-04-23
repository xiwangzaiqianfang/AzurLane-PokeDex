import json
import os
import hashlib
from PySide6.QtCore import QObject, Signal

class UserManager(QObject):
    user_changed = Signal(str)  # 用户名

    def __init__(self, base_dir="data/users"):
        super().__init__()
        self.base_dir = base_dir
        self.current_user = None
        self.user_list_file = os.path.join(base_dir, "user_list.json")
        self.users = {}  # {用户名: {"password_hash": str, "avatar": str}}
        self.load_user_list()

    def load_user_list(self):
        if os.path.exists(self.user_list_file):
            with open(self.user_list_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        else:
            os.makedirs(self.base_dir, exist_ok=True)
            self.users = {}
            self.save_user_list()

    def save_user_list(self):
        with open(self.user_list_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)

    def add_user(self, username, password=None, avatar=""):
        if username in self.users:
            return False
        user_dir = os.path.join(self.base_dir, username)
        os.makedirs(user_dir, exist_ok=True)
        password_hash = hashlib.sha256(password.encode()).hexdigest() if password else ""
        self.users[username] = {"password_hash": password_hash, "avatar": avatar}
        self.save_user_list()
        # 创建默认的用户状态文件
        state_file = os.path.join(user_dir, "ships_state.json")
        if not os.path.exists(state_file):
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump({"states": []}, f)
        return True

    def verify_password(self, username, password):
        if username not in self.users:
            return False
        stored_hash = self.users[username].get("password_hash", "")
        if not stored_hash:
            return True  # 无密码，直接通过
        return hashlib.sha256(password.encode()).hexdigest() == stored_hash

    def switch_user(self, username, password=None):
        if username not in self.users:
            return False
        if not self.verify_password(username, password):
            return False
        self.current_user = username
        self.user_changed.emit(username)
        return True

    def get_user_state_path(self, username=None):
        user = username or self.current_user
        if not user:
            return None
        return os.path.join(self.base_dir, user, "ships_state.json")

    def get_avatar_path(self, username):
        avatar = self.users[username].get("avatar", "")
        if avatar and os.path.exists(avatar):
            return avatar
        return None