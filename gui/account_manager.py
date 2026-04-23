# gui/account_manager.py
import json
import sys
import os
import hashlib
import datetime
from PySide6.QtCore import QObject, Signal,Qt
from PySide6.QtGui import QPixmap

SALT = "AzurLaneDex_Salt_2025"

def hash_password(password: str) -> str:
    if not password:
        return ""
    return hashlib.sha256((password + SALT).encode()).hexdigest()

def hash_answer(answer: str) -> str:
    return hashlib.sha256(answer.encode()).hexdigest()   # 简单哈希

class AccountManager(QObject):
    account_changed = Signal(str)

    def load(self):
        self.accounts = []   # 先初始化
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.accounts = data.get("accounts", [])
                    self.current_account = data.get("current_account")
            except:
                pass
        if not self.accounts:
            self._create_default_accounts()

    def __init__(self, accounts_file=None):
        super().__init__()
        if accounts_file is None:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.abspath(".")
            accounts_file = os.path.join(base_dir, "data", "users", "accounts.json")
        self.accounts_file = accounts_file
        self.accounts = []  
        self.current_account = None
        self.load()

    def load(self):
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.accounts = data.get("accounts", [])
                    self.current_account = data.get("current_account")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"加载账户文件失败: {e}")
                self.accounts = []
                self.current_account = None
        else:
            self._create_default_accounts()

    def _create_default_accounts(self):
        # 创建默认开发者账户，密码请自行修改
        dev_hash = hash_password("1029384756")
        dev_account = {
            "name": "developer",
            "password_hash": dev_hash,
            "avatar": "",
            "is_developer": True,
            "is_system": True,
            "security_question": "本账号仅用于开发，请勿随意尝试使用本账号",
            "security_answer_hash": "1029384756",
            "created": datetime.datetime.now().isoformat(),
            "last_login": ""
        }
        self.accounts.append(dev_account)
        self.current_account = "developer"
        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.accounts_file), exist_ok=True)
        data = {
            "accounts": self.accounts,
            "current_account": self.current_account
        }
        with open(self.accounts_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_account(self, name, password="", avatar="", is_developer=False):
        if any(acc["name"] == name for acc in self.accounts):
            return False
        account = {
            "name": name,
            "password_hash": hash_password(password),
            "avatar": avatar,
            "is_developer": is_developer,
            "security_question": "",
            "security_answer_hash": "",
            "created": datetime.datetime.now().isoformat(),
            "last_login": ""
        }
        self.accounts.append(account)
        self.save()
        return True

    def verify_password(self, name, password):
        for acc in self.accounts:
            if acc["name"] == name:
                return hash_password(password) == acc["password_hash"]
        return False

    def change_password(self, name, old_password, new_password):
        """修改密码，需提供旧密码"""
        for acc in self.accounts:
            if acc["name"] == name:
                if not self.verify_password(name, old_password):
                    return False
                acc["password_hash"] = hash_password(new_password)
                self.save()
                return True
        return False

    def reset_password_by_security(self, name, answer, new_password):
        """通过密保重置密码"""
        for acc in self.accounts:
            if acc["name"] == name:
                if acc["security_answer_hash"] and hash_answer(answer) == acc["security_answer_hash"]:
                    acc["password_hash"] = hash_password(new_password)
                    self.save()
                    return True
        return False

    def set_security_question(self, name, question, answer):
        """设置密保问题与答案"""
        for acc in self.accounts:
            if acc["name"] == name:
                acc["security_question"] = question
                acc["security_answer_hash"] = hash_answer(answer)
                self.save()
                return True
        return False

    def get_security_question(self, name):
        for acc in self.accounts:
            if acc["name"] == name:
                return acc.get("security_question", "")
        return ""

    def set_current_account(self, name):
        if name not in [acc["name"] for acc in self.accounts]:
            return False
        self.current_account = name
        for acc in self.accounts:
            if acc["name"] == name:
                acc["last_login"] = datetime.datetime.now().isoformat()
                break
        self.save()
        self.account_changed.emit(name)
        return True

    def get_current_account(self):
        return self.current_account

    def is_developer(self, name=None):
        if name is None:
            name = self.current_account
        for acc in self.accounts:
            if acc["name"] == name:
                return acc.get("is_developer", False)
        return False

    def delete_account(self, name):
        if name == "developer":
            return False
        self.accounts = [acc for acc in self.accounts if acc["name"] != name]
        if self.current_account == name:
            self.current_account = self.accounts[0]["name"] if self.accounts else None
        self.save()
        return True

    def get_account_list(self):
        return [acc["name"] for acc in self.accounts]

    def get_account_info(self, name):
        for acc in self.accounts:
            if acc["name"] == name:
                return acc
        return None
    
    def update_avatar(self, name, avatar_path):
        for acc in self.accounts:
            if acc["name"] == name:
                acc["avatar"] = avatar_path
                self.save()
                return True
        return False
    
    def save_avatar(self, account_name, source_path):
        """保存头像到 assets/user/账户名.png，返回保存后的路径"""
        avatars_dir = os.path.join(os.path.dirname(self.accounts_file), "avatars")
        os.makedirs(avatars_dir, exist_ok=True)
        dest_path = os.path.join(avatars_dir, f"{account_name}.png")
        pixmap = QPixmap(source_path)
        if pixmap.isNull():
            return ""
        pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap.save(dest_path)
        return dest_path

    def get_account_count(self):
        return len(self.accounts)
    
    def set_default_account(self, name):
        if name not in [acc["name"] for acc in self.accounts]:
            return False
        self.default_account = name
        self.save()
        return True
    
    def get_default_account(self):
        return getattr(self, 'default_account', None)
    
    def rename_account(self, old_name, new_name):
        if new_name in [acc["name"] for acc in self.accounts]:
            return False
        for acc in self.accounts:
            if acc["name"] == old_name:
                acc["name"] = new_name
                break
        # 重命名状态文件
        old_state = f"ships_state_{old_name}.json"
        new_state = f"ships_state_{new_name}.json"
        if os.path.exists(old_state):
            os.rename(old_state, new_state)
        # 重命名头像文件
        old_avatar = os.path.join("assets/user", f"{old_name}.png")
        new_avatar = os.path.join("assets/user", f"{new_name}.png")
        if os.path.exists(old_avatar):
            os.rename(old_avatar, new_avatar)
            for acc in self.accounts:
                if acc["name"] == new_name and acc.get("avatar") == old_avatar:
                    acc["avatar"] = new_avatar
                    break
        if self.default_account == old_name:
            self.default_account = new_name
        if self.current_account == old_name:
            self.current_account = new_name
        self.save()
        return True
    
    def get_regular_account_count(self):
        return len([acc for acc in self.accounts if not acc.get("is_system", False)])
    
    def set_developer_flag(self, account_name, is_developer):
        """设置指定账户的开发者标志（仅限开发者账户调用）"""
        # 权限检查：当前账户必须是开发者
        if not self.is_developer():
            raise PermissionError("只有开发者账户才能修改开发者标志")
        for acc in self.accounts:
            if acc["name"] == account_name:
                acc["is_developer"] = is_developer
                self.save()
                return True
        return False