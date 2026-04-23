# gui/account_dialog.py
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QPushButton,
                               QInputDialog, QMessageBox, QLineEdit, QHBoxLayout,
                               QLabel, QFileDialog, QWidget, QScrollArea, QListWidgetItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class AccountDialog(QDialog):
    def __init__(self, account_manager, dev_mode=False, parent=None):
        super().__init__(parent)
        self.account_manager = account_manager
        self.dev_mode = dev_mode
        self.setWindowTitle("账户管理")
        self.setModal(True)
        self.resize(400, 500)

        layout = QVBoxLayout(self)

        self.account_list = QListWidget()
        self.account_list.addItems(self.account_manager.get_account_list())
        layout.addWidget(self.account_list)

        # 操作按钮
        self.switch_btn = QPushButton("切换到此账户")
        self.switch_btn.clicked.connect(self.switch_account)
        layout.addWidget(self.switch_btn)

        self.new_btn = QPushButton("新建账户")
        self.new_btn.clicked.connect(self.new_account)
        layout.addWidget(self.new_btn)

        self.delete_btn = QPushButton("删除账户")
        self.delete_btn.clicked.connect(self.delete_account)
        layout.addWidget(self.delete_btn)

        self.modify_pwd_btn = QPushButton("修改当前账户密码")
        self.modify_pwd_btn.clicked.connect(self.modify_password)
        layout.addWidget(self.modify_pwd_btn)

        self.change_avatar_btn = QPushButton("更换头像")
        self.change_avatar_btn.clicked.connect(self.change_avatar)
        layout.addWidget(self.change_avatar_btn)

        self.rename_btn = QPushButton("重命名账户")
        self.rename_btn.clicked.connect(self.rename_account)
        layout.addWidget(self.rename_btn)

        self.set_admin_btn = QPushButton("设为管理员")
        self.set_admin_btn.clicked.connect(self.toggle_admin_status)
        layout.addWidget(self.set_admin_btn)

        self.set_security_btn = QPushButton("设置密保问题")
        self.set_security_btn.clicked.connect(self.set_security)
        layout.addWidget(self.set_security_btn)

        self.forgot_pwd_btn = QPushButton("忘记密码（密保重置）")
        self.forgot_pwd_btn.clicked.connect(self.forgot_password)
        layout.addWidget(self.forgot_pwd_btn)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)

        self.refresh_account_list()

    def get_selected_account(self):
        item = self.account_list.currentItem()
        if item:
            return item.data(Qt.UserRole)  # 返回原始账户名
        return item.text() if item else None

    def switch_account(self):
        name = self.get_selected_account()
        print(f"选中的账户: {name}")
        if not name:
            return
        # 需要密码验证
        if self.account_manager.verify_password(name, self.get_password(name)):
            self.account_manager.set_current_account(name)
            QMessageBox.information(self, "成功", f"已切换到账户 {name}")
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "密码错误")

    def get_password(self, account_name):
        for acc in self.account_manager.accounts:
            if acc["name"] == account_name and acc["password_hash"]:
                print(f"账户 {account_name} 的密码哈希: {acc.get('password_hash')}")
                pwd, ok = QInputDialog.getText(self, "输入密码", f"账户 {account_name} 需要密码:", QLineEdit.Password)
                if ok:
                    return pwd
                else:
                    return None
        return ""

    def new_account(self):
        # 输入账户名
        name, ok = QInputDialog.getText(self, "新建账户", "账户名:")
        if not ok or not name:
            return
        if self.account_manager.get_account_info(name):
            QMessageBox.warning(self, "错误", "账户名已存在")
            return
        # 密码
        pwd, ok = QInputDialog.getText(self, "设置密码", "密码（可选）:", QLineEdit.Password)
        if not ok:
            pwd = ""
        # 选择头像
        avatar_path = self.select_avatar(name)
        # 是否设为开发者账户（仅当当前账户是开发者时显示）
        is_dev = False
        if self.account_manager.is_developer():
            reply = QMessageBox.question(self, "权限", "是否设为开发者账户？", QMessageBox.Yes | QMessageBox.No)
            is_dev = (reply == QMessageBox.Yes)
        # 创建账户
        if self.account_manager.add_account(name, pwd, avatar=avatar_path, is_developer=is_dev):
            self.account_list.addItem(name)
            QMessageBox.information(self, "成功", f"账户 {name} 已创建")
        else:
            QMessageBox.warning(self, "错误", "账户名已存在")

    def select_avatar(self, account_name):
        """打开文件选择对话框，选择头像图片，并复制到 avatars 目录"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择头像", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not file_path:
            return ""
        return self.account_manager.save_avatar(account_name, file_path)
    
    def change_avatar(self):
        item = self.account_list.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请先选择一个账户")
            return
        account_name = item.text()
        # 验证密码（如果是当前账户且设置了密码，需要验证）
        if account_name == self.account_manager.get_current_account():
            if self.account_manager.verify_password(account_name, self.get_password(account_name)) is False:
                QMessageBox.warning(self, "错误", "密码错误")
                return
        new_avatar_path = self.select_avatar(account_name)
        if new_avatar_path:
            # 更新账户信息中的头像路径
            for acc in self.account_manager.accounts:
                if acc["name"] == account_name:
                    acc["avatar"] = new_avatar_path
                    self.account_manager.save()
                    QMessageBox.information(self, "成功", "头像已更新")
                    # 如果更新的是当前账户，刷新主窗口显示
                    if account_name == self.account_manager.get_current_account() and self.parent():
                        self.parent().update_avatar_display()
                    break

    def delete_account(self):
        name = self.get_selected_account()
        if not name:
            return
        if name == "developer":
            QMessageBox.warning(self, "禁止", "不能删除系统账户")
            return
        if self.account_manager.is_developer() or name == self.account_manager.get_current_account():
            reply = QMessageBox.question(self, "确认", f"删除账户 {name} 会永久丢失其数据，是否继续？",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.account_manager.delete_account(name)
                self.account_list.takeItem(self.account_list.row(self.account_list.currentItem()))
                QMessageBox.information(self, "成功", "账户已删除")
        else:
            QMessageBox.warning(self, "权限不足", "只有开发者或当前账户本人才能删除")

    def modify_password(self):
        current = self.account_manager.get_current_account()
        old_pwd, ok = QInputDialog.getText(self, "修改密码", "请输入旧密码:", QLineEdit.Password)
        if not ok:
            return
        new_pwd, ok = QInputDialog.getText(self, "修改密码", "请输入新密码:", QLineEdit.Password)
        if not ok:
            return
        if self.account_manager.change_password(current, old_pwd, new_pwd):
            QMessageBox.information(self, "成功", "密码已修改")
        else:
            QMessageBox.warning(self, "错误", "旧密码错误")

    def set_security(self):
        current = self.account_manager.get_current_account()
        question, ok = QInputDialog.getText(self, "设置密保", "请输入密保问题:")
        if not ok:
            return
        answer, ok = QInputDialog.getText(self, "设置密保", "请输入答案:")
        if not ok:
            return
        if self.account_manager.set_security_question(current, question, answer):
            QMessageBox.information(self, "成功", "密保已设置")
        else:
            QMessageBox.warning(self, "错误", "设置失败")

    def forgot_password(self):
        name = self.get_selected_account()
        if not name:
            name = self.account_manager.get_current_account()
        if not name:
            return
        question = self.account_manager.get_security_question(name)
        if not question:
            QMessageBox.warning(self, "提示", "该账户未设置密保问题，无法重置密码")
            return
        answer, ok = QInputDialog.getText(self, "重置密码", f"密保问题：{question}\n请输入答案:", QLineEdit.Normal)
        if not ok:
            return
        new_pwd, ok = QInputDialog.getText(self, "重置密码", "请输入新密码:", QLineEdit.Password)
        if not ok:
            return
        if self.account_manager.reset_password_by_security(name, answer, new_pwd):
            QMessageBox.information(self, "成功", "密码已重置，请使用新密码登录")
        else:
            QMessageBox.warning(self, "错误", "答案错误")

    def refresh_account_list(self):
        print(f"刷新账户列表，dev_mode={self.dev_mode}")
        self.account_list.clear()
        for acc in self.account_manager.accounts:
            if not self.dev_mode and acc.get("is_system", False):
                continue
            display_name = acc["name"]
            if acc.get("is_developer", False):
                display_name += " (管理员)"
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, acc["name"])
            self.account_list.addItem(item)

    def rename_account(self):
        item = self.account_list.currentItem()
        if not item:
            return
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, "重命名账户", "新账户名:", text=old_name)
        if not ok or not new_name or new_name == old_name:
            return
        if self.account_manager.rename_account(old_name, new_name):
            self.refresh_account_list()
            if self.account_manager.get_current_account() == new_name and self.parent():
                self.parent().update_avatar_display()
            QMessageBox.information(self, "成功", "账户已重命名")
        else:
            QMessageBox.warning(self, "错误", "重命名失败，可能名称已存在")

    def toggle_admin_status(self):
        item = self.account_list.currentItem()
        if not item:
            return
        account_name = item.text()
        # 不能修改当前登录账户的开发者状态（防止自己降级）
        if account_name == self.account_manager.get_current_account():
            QMessageBox.warning(self, "提示", "不能修改当前登录账户的权限")
            return
        # 只有开发者账户才能执行此操作
        if not self.account_manager.is_developer():
            QMessageBox.warning(self, "权限不足", "只有管理员才能修改其他账户的权限")
            return
        current = self.account_manager.get_account_info(account_name).get("is_developer", False)
        new_status = not current
        if self.account_manager.set_developer_flag(account_name, new_status):
            QMessageBox.information(self, "成功", f"账户 {account_name} 已{'授予' if new_status else '撤销'}管理员权限")
            # 刷新列表显示（可选）
            self.refresh_account_list()
        else:
            QMessageBox.warning(self, "错误", "操作失败")