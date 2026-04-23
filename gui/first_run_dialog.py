from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QCheckBox, QPushButton, QDialogButtonBox, QFileDialog, QMessageBox, QLabel
from PySide6.QtCore import Qt

class FirstRunDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("初始化账户")
        self.setModal(True)
        layout = QVBoxLayout(self)

        info_label = QLabel("为了您的使用体验，请先创建一个本地帐户用于保存数据")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("账户名")
        form.addRow("账户名:", self.name_edit)

        self.pwd_edit = QLineEdit()
        self.pwd_edit.setPlaceholderText("密码（可选）")
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        form.addRow("密码:", self.pwd_edit)

        #self.is_dev_cb = QCheckBox("设为管理员账户（仅开发模式可用）")
        #form.addRow("", self.is_dev_cb)

        self.default_cb = QCheckBox("设为默认账户（自动登录）")
        form.addRow("", self.default_cb)

        layout.addLayout(form)

        self.avatar_btn = QPushButton("选择头像")
        self.avatar_btn.clicked.connect(self.select_avatar)
        layout.addWidget(self.avatar_btn)
        self.avatar_path = ""

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def select_avatar(self):
        reply = QMessageBox.question(
            self, 
            "选择头像", 
            "您可以选择一张图片作为您的头像（可选）。\n\n是否现在选择？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择头像", "", "Images (*.png *.jpg *.jpeg *.bmp)")
            if file_path:
                self.avatar_path = file_path
                self.avatar_btn.setText("已选择头像")
        else:
            pass

    def get_account_info(self):
        return {
            "name": self.name_edit.text().strip(),
            "password": self.pwd_edit.text(),
            "is_developer": False,
            "avatar": self.avatar_path,
            "set_default": self.default_cb.isChecked()
        }